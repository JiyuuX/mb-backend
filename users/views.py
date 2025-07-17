from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import CustomUser
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserUpdateSerializer, EmailVerificationSerializer, PasswordChangeSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    PublicProfileSerializer, FollowSerializer
)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsNotBanned

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Email aktivasyon mesajı gönder
            self.send_verification_email(user)
            
            return Response({
                'message': 'Kayıt başarılı! Email adresinizi doğrulamanız gerekiyor.',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def send_verification_email(self, user):
        """Email aktivasyon mesajı gönderir"""
        user.email_verification_sent_at = timezone.now()
        user.save()
        
        verification_url = f"http://localhost:8000/api/users/verify-email/{user.email_verification_token}/"
        
        subject = 'Email Adresinizi Doğrulayın'
        html_message = f"""
        <h2>Hoş Geldiniz!</h2>
        <p>Email adresinizi doğrulamak için aşağıdaki linke tıklayın:</p>
        <a href="{verification_url}">Email Adresimi Doğrula</a>
        <p>Bu link 24 saat geçerlidir.</p>
        """
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            'noreply@hpgenc.com',
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # JWT token oluştur
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Giriş başarılı!',
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                },
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_premium': user.is_premium,
                    'is_premium_active': user.is_premium_active,
                    'email_verified': user.email_verified,
                    'profile_picture': user.profile_picture.url if user.profile_picture else None,
                    'bio': user.bio,
                    'phone_number': user.phone_number,
                    'custom_username_color': user.custom_username_color,
                    'card_number': user.card_number,
                    'card_issued_at': user.card_issued_at.isoformat() if user.card_issued_at else None,
                    'can_create_threads': user.can_create_threads,
                    'is_secondhand_seller': user.is_secondhand_seller,
                    'instagram': user.instagram,
                    'twitter': user.twitter,
                    'facebook': user.facebook,
                    'linkedin': user.linkedin,
                    'website': user.website,
                    'followers_count': user.followers.count(),
                    'following_count': user.following.count(),
                    'is_following': False,  # Kendisi kendisini takip etmez
                    'created_at': user.date_joined.isoformat(),
                    'updated_at': user.updated_at.isoformat() if hasattr(user, 'updated_at') else user.date_joined.isoformat(),
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EmailVerificationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, token):
        try:
            user = CustomUser.objects.get(email_verification_token=token)
            
            # Token'ın geçerlilik süresini kontrol et (24 saat)
            if user.email_verification_sent_at:
                time_diff = timezone.now() - user.email_verification_sent_at
                if time_diff.total_seconds() > 86400:  # 24 saat
                    return Response({
                        'message': 'Email doğrulama linki süresi dolmuş. Yeni bir link talep edin.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            user.email_verified = True
            user.save()
            
            return Response({
                'message': 'Email adresiniz başarıyla doğrulandı! Şimdi giriş yapabilirsiniz.'
            }, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            return Response({
                'message': 'Geçersiz doğrulama linki.'
            }, status=status.HTTP_400_BAD_REQUEST)

class ResendVerificationEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({
                'message': 'Email adresi gereklidir.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(email=email)
            if user.email_verified:
                return Response({
                    'message': 'Bu email adresi zaten doğrulanmış.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Yeni token oluştur
            user.email_verification_token = user.email_verification_token
            user.save()
            
            # Email gönder
            self.send_verification_email(user)
            
            return Response({
                'message': 'Doğrulama emaili tekrar gönderildi.'
            }, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            return Response({
                'message': 'Bu email adresi ile kayıtlı kullanıcı bulunamadı.'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def send_verification_email(self, user):
        """Email aktivasyon mesajı gönderir"""
        user.email_verification_sent_at = timezone.now()
        user.save()
        
        verification_url = f"http://localhost:8000/api/users/verify-email/{user.email_verification_token}/"
        
        subject = 'Email Adresinizi Doğrulayın'
        html_message = f"""
        <h2>Email Doğrulama</h2>
        <p>Email adresinizi doğrulamak için aşağıdaki linke tıklayın:</p>
        <a href="{verification_url}">Email Adresimi Doğrula</a>
        <p>Bu link 24 saat geçerlidir.</p>
        """
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            'noreply@hpgenc.com',
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def get_object(self):
        return self.request.user

class PasswordChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']
            
            if not user.check_password(old_password):
                return Response({
                    'message': 'Mevcut şifre yanlış.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(new_password)
            user.save()
            
            return Response({
                'message': 'Şifre başarıyla değiştirildi.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Başarıyla çıkış yapıldı.'
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                'message': 'Çıkış yapılırken bir hata oluştu.'
            }, status=status.HTTP_400_BAD_REQUEST)

class ActivatePremiumView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def post(self, request):
        try:
            user = request.user
            
            # Premium üyeliği aktifleştir (30 gün)
            user.activate_premium(duration_days=30)
            
            # Kart numarası oluştur
            card_number = user.generate_card_number()
            
            return Response({
                'message': 'Premium üyeliğiniz başarıyla aktifleştirildi!',
                'is_premium': True,
                'premium_expires_at': user.premium_expires_at.isoformat(),
                'card_number': card_number,
                'can_create_threads': True,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message': f'Premium aktivasyon hatası: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsNotBanned]

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated, IsNotBanned])
    def activate_secondhand_seller(self, request):
        user = request.user
        user.is_secondhand_seller = True
        user.save()
        return Response({'success': True, 'message': '2. el satıcı badge aktif edildi.'})

class PublicProfileView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, username):
        try:
            user = CustomUser.objects.get(username=username)
            serializer = PublicProfileSerializer(user, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({
                'message': 'Kullanıcı bulunamadı.'
            }, status=status.HTTP_404_NOT_FOUND)

class FollowUserView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def post(self, request):
        serializer = FollowSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            action = serializer.validated_data['action']
            
            try:
                target_user = CustomUser.objects.get(id=user_id)
                
                if action == 'follow':
                    if request.user != target_user:
                        request.user.following.add(target_user)
                        message = f'{target_user.username} kullanıcısını takip etmeye başladınız.'
                    else:
                        return Response({
                            'message': 'Kendinizi takip edemezsiniz.'
                        }, status=status.HTTP_400_BAD_REQUEST)
                elif action == 'unfollow':
                    request.user.following.remove(target_user)
                    message = f'{target_user.username} kullanıcısını takipten çıkardınız.'
                
                return Response({
                    'message': message,
                    'is_following': action == 'follow'
                }, status=status.HTTP_200_OK)
                
            except CustomUser.DoesNotExist:
                return Response({
                    'message': 'Kullanıcı bulunamadı.'
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserFollowersView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, username):
        try:
            user = CustomUser.objects.get(username=username)
            followers = user.followers.all()
            serializer = PublicProfileSerializer(followers, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({
                'message': 'Kullanıcı bulunamadı.'
            }, status=status.HTTP_404_NOT_FOUND)

class UserFollowingView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, username):
        try:
            user = CustomUser.objects.get(username=username)
            following = user.following.all()
            serializer = PublicProfileSerializer(following, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({
                'message': 'Kullanıcı bulunamadı.'
            }, status=status.HTTP_404_NOT_FOUND)
