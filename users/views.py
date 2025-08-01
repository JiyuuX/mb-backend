from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import CustomUser, Notification
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserUpdateSerializer, EmailVerificationSerializer, PasswordChangeSerializer,
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer,
    PublicProfileSerializer, FollowSerializer, UserSerializer, NotificationSerializer
)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import IsNotBanned
from django.db.models import Count, Q

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # 6 haneli doğrulama kodu oluştur
            verification_code = user.generate_verification_code()
            
            # Kodu backend'de printle (şimdilik)
            print(f"Kullanıcı {user.email} için doğrulama kodu: {verification_code}")
            
            return Response({
                'message': 'Kayıt başarılı! Email adresinizi doğrulamanız gerekiyor.',
                'user_id': user.id,
                'verification_code': verification_code,  # Frontend'de göstermek için
                'email': user.email
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
            
            # Email doğrulanmış mı kontrol et
            if not user.email_verified:
                # Yeni kod oluştur
                verification_code = user.generate_verification_code()
                print(f"Giriş denemesi - Kullanıcı {user.email} için doğrulama kodu: {verification_code}")
                
                return Response({
                    'message': 'Email adresinizi doğrulamanız gerekiyor.',
                    'email_verification_required': True,
                    'verification_code': verification_code,
                    'email': user.email
                }, status=status.HTTP_401_UNAUTHORIZED)
            
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
    
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response({
                'message': 'Email ve doğrulama kodu gereklidir.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = CustomUser.objects.get(email=email)
            
            # Kodun süresi dolmuş mu kontrol et
            if user.is_verification_code_expired():
                return Response({
                    'message': 'Doğrulama kodunun süresi dolmuş. Yeni bir kod talep edin.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Kodu kontrol et
            if user.email_verification_code != code:
                return Response({
                    'message': 'Geçersiz doğrulama kodu.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Email'i doğrula
            user.email_verified = True
            user.email_verification_code = None  # Kodu temizle
            user.save()
            
            return Response({
                'message': 'Email adresiniz başarıyla doğrulandı! Şimdi giriş yapabilirsiniz.'
            }, status=status.HTTP_200_OK)
            
        except CustomUser.DoesNotExist:
            return Response({
                'message': 'Bu email adresi ile kayıtlı kullanıcı bulunamadı.'
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
            
            # Yeni kod oluştur
            verification_code = user.generate_verification_code()
            
            # Kodu backend'de printle (şimdilik)
            print(f"Kullanıcı {user.email} için yeni doğrulama kodu: {verification_code}")
            
            return Response({
                'message': 'Yeni doğrulama kodu oluşturuldu.',
                'verification_code': verification_code,  # Frontend'de göstermek için
                'email': user.email
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
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        
        # Profil fotoğrafı değişikliği kontrolü
        if 'profile_picture' in request.data and request.data['profile_picture']:
            # Eğer yeni bir profil fotoğrafı yükleniyorsa
            if not user.can_change_profile_picture():
                return Response({
                    'message': 'Gün içerisinde maksimum 2 kez profil fotoğrafı değiştirebilirsiniz.',
                    'error': 'PROFILE_PICTURE_LIMIT_EXCEEDED'
                }, status=status.HTTP_400_BAD_REQUEST)
            # GIF kontrolü
            file = request.data['profile_picture']
            if hasattr(file, 'content_type'):
                is_gif = file.content_type == 'image/gif'
            else:
                is_gif = str(file).lower().endswith('.gif')
            if is_gif and not user.is_premium:
                return Response({
                    'message': 'Sadece Premium üyeler GIF profil resmine sahip olabilir.',
                    'error': 'GIF_PROFILE_PICTURE_PREMIUM_ONLY'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Profil güncellemesini yap
        response = super().update(request, *args, **kwargs)
        
        # Eğer profil fotoğrafı başarıyla güncellendiyse kaydet
        if response.status_code == 200 and 'profile_picture' in request.data and request.data['profile_picture']:
            user.record_profile_picture_change()
        
        return response

class UserUpdateView(generics.UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        
        # Profil fotoğrafı değişikliği kontrolü
        if 'profile_picture' in request.data and request.data['profile_picture']:
            # Eğer yeni bir profil fotoğrafı yükleniyorsa
            if not user.can_change_profile_picture():
                return Response({
                    'message': 'Gün içerisinde maksimum 2 kez profil fotoğrafı değiştirebilirsiniz.',
                    'error': 'PROFILE_PICTURE_LIMIT_EXCEEDED'
                }, status=status.HTTP_400_BAD_REQUEST)
            # GIF kontrolü
            file = request.data['profile_picture']
            if hasattr(file, 'content_type'):
                is_gif = file.content_type == 'image/gif'
            else:
                is_gif = str(file).lower().endswith('.gif')
            if is_gif and not user.is_premium:
                return Response({
                    'message': 'Sadece Premium üyeler GIF profil resmine sahip olabilir.',
                    'error': 'GIF_PROFILE_PICTURE_PREMIUM_ONLY'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Profil güncellemesini yap
        response = super().update(request, *args, **kwargs)
        
        # Eğer profil fotoğrafı başarıyla güncellendiyse kaydet
        if response.status_code == 200 and 'profile_picture' in request.data and request.data['profile_picture']:
            user.record_profile_picture_change()
        
        return response

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
                        # Takip işlemi
                        request.user.following.add(target_user)
                        message = f'{target_user.username} kullanıcısını takip etmeye başladınız.'
                        
                        # Takip bildirimi oluştur
                        Notification.create_follow_notification(request.user, target_user)
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

class UpdateUsernameColorView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def post(self, request):
        user = request.user
        
        # Sadece premium kullanıcılar renk değiştirebilir
        if not user.is_premium_active:
            return Response({
                'message': 'Bu özellik sadece premium kullanıcılar için geçerlidir.',
                'error': 'PREMIUM_REQUIRED'
            }, status=status.HTTP_403_FORBIDDEN)
        
        color = request.data.get('color')
        if not color:
            return Response({
                'message': 'Renk kodu gereklidir.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Renk formatını kontrol et (hex format)
        if not color.startswith('#') or len(color) != 7:
            return Response({
                'message': 'Geçersiz renk formatı. Hex formatında olmalıdır (örn: #FF0000).'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Siyah ve beyaz renkleri engelle
        if color.upper() in ['#000000', '#FFFFFF', '#000', '#FFF']:
            return Response({
                'message': 'Siyah ve beyaz renkler kullanılamaz.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user.custom_username_color = color
            user.save()
            
            return Response({
                'message': 'Kullanıcı adı rengi başarıyla güncellendi.',
                'custom_username_color': color
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message': f'Renk güncellenirken hata oluştu: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)

class RequestNameChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def post(self, request):
        try:
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            
            if not first_name and not last_name:
                return Response({
                    'message': 'En az bir alan (isim veya soyisim) gereklidir.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = request.user
            
            # Doğrulama kodu oluştur
            verification_code = user.generate_verification_code()
            
            # Kodu backend'de printle (şimdilik)
            print(f"İsim değişikliği - Kullanıcı {user.email} için doğrulama kodu: {verification_code}")
            
            # Geçici olarak kodu user model'inde sakla
            user.temp_verification_code = verification_code
            user.temp_first_name = first_name
            user.temp_last_name = last_name
            user.temp_verification_expires = timezone.now() + timedelta(minutes=5)
            user.save()
            
            print(f"DEBUG - User model saved for user {user.email}")
            print(f"DEBUG - Stored code: {user.temp_verification_code}")
            print(f"DEBUG - Stored first_name: {user.temp_first_name}")
            print(f"DEBUG - Stored last_name: {user.temp_last_name}")
            print(f"DEBUG - Stored expires: {user.temp_verification_expires}")
            
            return Response({
                'message': 'Doğrulama kodu e-posta adresinize gönderildi.',
                'verification_code': verification_code,  # Frontend'de göstermek için
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message': f'İsim değişikliği isteği gönderilemedi: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyNameChangeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def post(self, request):
        try:
            verification_code = request.data.get('verification_code')
            
            if not verification_code:
                return Response({
                    'message': 'Doğrulama kodu gereklidir.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user = request.user
            
            # User model'inden geçici kodları kontrol et
            stored_code = user.temp_verification_code
            stored_first_name = user.temp_first_name
            stored_last_name = user.temp_last_name
            stored_expires = user.temp_verification_expires
            
            print(f"DEBUG - Verification attempt for user {user.email}")
            print(f"DEBUG - Received code: {verification_code}")
            print(f"DEBUG - Stored code: {stored_code}")
            print(f"DEBUG - Stored first_name: {stored_first_name}")
            print(f"DEBUG - Stored last_name: {stored_last_name}")
            print(f"DEBUG - Stored expires: {stored_expires}")
            
            if not stored_code or not stored_expires:
                return Response({
                    'message': 'Doğrulama kodu bulunamadı veya süresi dolmuş.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Süre kontrolü
            if timezone.now() > stored_expires:
                # Süresi dolmuş kodları temizle
                user.temp_verification_code = None
                user.temp_first_name = None
                user.temp_last_name = None
                user.temp_verification_expires = None
                user.save()
                return Response({
                    'message': 'Doğrulama kodunun süresi dolmuş.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Kod kontrolü
            if verification_code != stored_code:
                return Response({
                    'message': 'Doğrulama kodu hatalı.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # İsim değişikliklerini uygula
            if stored_first_name is not None:
                user.first_name = stored_first_name
            if stored_last_name is not None:
                user.last_name = stored_last_name
            
            # Geçici kodları temizle
            user.temp_verification_code = None
            user.temp_first_name = None
            user.temp_last_name = None
            user.temp_verification_expires = None
            user.save()
            
            return Response({
                'message': 'İsim ve soyisim başarıyla güncellendi.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'message': f'İsim güncellenirken hata oluştu: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DeleteAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def post(self, request):
        password = request.data.get('password')
        
        if not password:
            return Response({
                'message': 'Şifre gereklidir.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kullanıcının şifresini doğrula
        user = request.user
        if not user.check_password(password):
            return Response({
                'message': 'Şifre yanlış.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Kullanıcıyı sil
        user.delete()
        
        return Response({
            'message': 'Hesabınız başarıyla silindi.'
        }, status=status.HTTP_200_OK)

class UniversityListView(APIView):
    def get(self, request):
        universities = [
            "Abant İzzet Baysal Üniversitesi",
            "Adana Alparslan Türkeş Bilim ve Teknoloji Üniversitesi",
            "Adıyaman Üniversitesi",
            "Afyon Kocatepe Üniversitesi",
            "Afyonkarahisar Sağlık Bilimleri Üniversitesi",
            "Ağrı İbrahim Çeçen Üniversitesi",
            "Aksaray Üniversitesi",
            "Alanya Alaaddin Keykubat Üniversitesi",
            "Amasya Üniversitesi",
            "Anadolu Üniversitesi",
            "Ankara Hacı Bayram Veli Üniversitesi",
            "Ankara Üniversitesi",
            "Ankara Yıldırım Beyazıt Üniversitesi",
            "Antalya Bilim Üniversitesi",
            "Ardahan Üniversitesi",
            "Artvin Çoruh Üniversitesi",
            "Atatürk Üniversitesi",
            "Balıkesir Üniversitesi",
            "Bandırma Onyedi Eylül Üniversitesi",
            "Bartın Üniversitesi",
            "Batman Üniversitesi",
            "Bayburt Üniversitesi",
            "Bilecik Şeyh Edebali Üniversitesi",
            "Bingöl Üniversitesi",
            "Bitlis Eren Üniversitesi",
            "Boğaziçi Üniversitesi",
            "Bolu Abant İzzet Baysal Üniversitesi",
            "Burdur Mehmet Akif Ersoy Üniversitesi",
            "Bursa Teknik Üniversitesi",
            "Bursa Uludağ Üniversitesi",
            "Çanakkale Onsekiz Mart Üniversitesi",
            "Çankırı Karatekin Üniversitesi",
            "Çukurova Üniversitesi",
            "Dicle Üniversitesi",
            "Düzce Üniversitesi",
            "Ege Üniversitesi",
            "Erciyes Üniversitesi",
            "Erzincan Binali Yıldırım Üniversitesi",
            "Erzurum Teknik Üniversitesi",
            "Eskişehir Osmangazi Üniversitesi",
            "Eskişehir Teknik Üniversitesi",
            "Fırat Üniversitesi",
            "Galatasaray Üniversitesi",
            "Gaziantep Üniversitesi",
            "Gaziosmanpaşa Üniversitesi",
            "Gebze Teknik Üniversitesi",
            "Giresun Üniversitesi",
            "Gümüşhane Üniversitesi",
            "Hacettepe Üniversitesi",
            "Hakkari Üniversitesi",
            "Harran Üniversitesi",
            "Hatay Mustafa Kemal Üniversitesi",
            "Hitit Üniversitesi",
            "Iğdır Üniversitesi",
            "Isparta Uygulamalı Bilimler Üniversitesi",
            "İnönü Üniversitesi",
            "İskenderun Teknik Üniversitesi",
            "İstanbul Medeniyet Üniversitesi",
            "İstanbul Teknik Üniversitesi",
            "İstanbul Üniversitesi",
            "İstanbul Üniversitesi-Cerrahpaşa",
            "İzmir Bakırçay Üniversitesi",
            "İzmir Demokrasi Üniversitesi",
            "İzmir Katip Çelebi Üniversitesi",
            "İzmir Yüksek Teknoloji Enstitüsü",
            "Kafkas Üniversitesi",
            "Kahramanmaraş Sütçü İmam Üniversitesi",
            "Karabük Üniversitesi",
            "Karadeniz Teknik Üniversitesi",
            "Karamanoğlu Mehmetbey Üniversitesi",
            "Kastamonu Üniversitesi",
            "Kayseri Üniversitesi",
            "Kırıkkale Üniversitesi",
            "Kırklareli Üniversitesi",
            "Kırşehir Ahi Evran Üniversitesi",
            "Kilis 7 Aralık Üniversitesi",
            "Kocaeli Üniversitesi",
            "Konya Teknik Üniversitesi",
            "KTO Karatay Üniversitesi",
            "Malatya Turgut Özal Üniversitesi",
            "Manisa Celal Bayar Üniversitesi",
            "Mardin Artuklu Üniversitesi",
            "Marmara Üniversitesi",
            "Mersin Üniversitesi",
            "Muğla Sıtkı Koçman Üniversitesi",
            "Munzur Üniversitesi",
            "Muş Alparslan Üniversitesi",
            "Nevşehir Hacı Bektaş Veli Üniversitesi",
            "Niğde Ömer Halisdemir Üniversitesi",
            "Ondokuz Mayıs Üniversitesi",
            "Ordu Üniversitesi",
            "Osmaniye Korkut Ata Üniversitesi",
            "Pamukkale Üniversitesi",
            "Recep Tayyip Erdoğan Üniversitesi",
            "Sakarya Üniversitesi",
            "Samsun Üniversitesi",
            "Siirt Üniversitesi",
            "Sinop Üniversitesi",
            "Sivas Cumhuriyet Üniversitesi",
            "Süleyman Demirel Üniversitesi",
            "Şırnak Üniversitesi",
            "Tekirdağ Namık Kemal Üniversitesi",
            "Tokat Gaziosmanpaşa Üniversitesi",
            "Trabzon Üniversitesi",
            "Trakya Üniversitesi",
            "Tunceli Munzur Üniversitesi",
            "Uşak Üniversitesi",
            "Van Yüzüncü Yıl Üniversitesi",
            "Yalova Üniversitesi",
            "Yıldız Teknik Üniversitesi",
            "Yozgat Bozok Üniversitesi",
            "Zonguldak Bülent Ecevit Üniversitesi"
        ]
        return Response({"universities": universities})

@api_view(['GET'])
def popular_users(request):
    """Aylık en popüler 10 kullanıcıyı döndürür"""
    try:
        # Son 30 günün tarihini hesapla
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Popüler kullanıcıları hesapla
        popular_users = CustomUser.objects.filter(
            is_active=True,
            is_banned=False
        ).annotate(
            # Thread beğeni sayısı
            thread_likes=Count('threads__likes', filter=Q(threads__created_at__gte=thirty_days_ago)),
            # Yeni takipçi sayısı
            new_followers=Count('followers', filter=Q(followers__date_joined__gte=thirty_days_ago)),
            # Toplam popülerlik puanı
            popularity=Count('threads__likes', filter=Q(threads__created_at__gte=thirty_days_ago)) + 
                     Count('followers', filter=Q(followers__date_joined__gte=thirty_days_ago)) * 2
        ).filter(
            popularity__gt=0
        ).order_by('-popularity')[:10]
        
        serializer = PublicProfileSerializer(popular_users, many=True, context={'request': request})
        return Response(serializer.data)
        
    except Exception as e:
        return Response({
            'error': 'Popüler kullanıcılar yüklenirken hata oluştu.',
            'detail': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotificationListView(APIView):
    """Kullanıcının bildirimlerini listeler"""
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def get(self, request):
        try:
            notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
            serializer = NotificationSerializer(notifications, many=True)
            
            # Okunmamış bildirim sayısını hesapla
            unread_count = notifications.filter(is_read=False).count()
            
            return Response({
                'notifications': serializer.data,
                'unread_count': unread_count,
                'total_count': notifications.count()
            })
        except Exception as e:
            return Response({
                'error': 'Bildirimler yüklenirken hata oluştu.',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MarkNotificationsAsReadView(APIView):
    """Tüm bildirimleri okundu olarak işaretler"""
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def post(self, request):
        try:
            # Kullanıcının tüm bildirimlerini okundu olarak işaretle
            Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
            
            return Response({
                'message': 'Tüm bildirimler okundu olarak işaretlendi.'
            })
        except Exception as e:
            return Response({
                'error': 'Bildirimler güncellenirken hata oluştu.',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UnreadNotificationCountView(APIView):
    """Okunmamış bildirim sayısını döndürür"""
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def get(self, request):
        try:
            unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
            return Response({
                'unread_count': unread_count
            })
        except Exception as e:
            return Response({
                'error': 'Bildirim sayısı alınırken hata oluştu.',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
