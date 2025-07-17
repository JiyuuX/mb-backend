from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Şifreler eşleşmiyor.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Geçersiz kullanıcı adı veya şifre.')
            if not user.is_active:
                raise serializers.ValidationError('Hesabınız aktif değil.')
            if not user.email_verified:
                raise serializers.ValidationError('Email adresinizi doğrulamanız gerekiyor.')
            # Ban kontrolü
            if user.is_banned:
                from django.utils import timezone
                now = timezone.now()
                if user.ban_until is None or (user.ban_until and user.ban_until > now):
                    kalan_sure = None
                    if user.ban_until:
                        kalan_sure = user.ban_until - now
                    raise serializers.ValidationError({
                        'banli': True,
                        'ban_sebebi': user.ban_reason,
                        'ban_suresiz': user.ban_until is None,
                        'ban_bitis': user.ban_until,
                        'kalan_sure': kalan_sure.total_seconds() if kalan_sure else None,
                        'mesaj': f"Hesabınız {'süresiz' if user.ban_until is None else 'süreli'} olarak banlanmıştır. {f'Kalan süre: {kalan_sure}' if kalan_sure else ''}"
                    })
        else:
            raise serializers.ValidationError('Kullanıcı adı ve şifre gereklidir.')
        
        attrs['user'] = user
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    is_premium_active = serializers.ReadOnlyField()
    email_verified = serializers.ReadOnlyField()
    card_issued_at = serializers.ReadOnlyField()
    instagram = serializers.ReadOnlyField()
    twitter = serializers.ReadOnlyField()
    facebook = serializers.ReadOnlyField()
    linkedin = serializers.ReadOnlyField()
    website = serializers.ReadOnlyField()
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    is_following = serializers.SerializerMethodField()
    created_at = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    thread_count = serializers.ReadOnlyField()
    is_banned = serializers.ReadOnlyField()
    ban_reason = serializers.ReadOnlyField()
    ban_until = serializers.ReadOnlyField()
    
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 
                 'bio', 'phone_number', 'is_premium', 'is_premium_active', 'email_verified',
                 'premium_expires_at', 'custom_username_color', 'card_number', 'card_issued_at',
                 'can_create_threads', 'is_secondhand_seller', 'instagram', 'twitter', 
                 'facebook', 'linkedin', 'website', 'followers_count', 'following_count',
                 'is_following', 'created_at', 'updated_at', 'thread_count',
                 'is_banned', 'ban_reason', 'ban_until')
        read_only_fields = ('id', 'username', 'email', 'is_premium', 'is_premium_active',
                           'email_verified', 'premium_expires_at', 'card_number', 'card_issued_at',
                           'can_create_threads', 'created_at', 'updated_at',
                           'is_banned', 'ban_reason', 'ban_until')
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.followers.all()
        return False

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'profile_picture', 'bio', 'phone_number', 'custom_username_color')

class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.UUIDField()

class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Yeni şifreler eşleşmiyor.")
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Yeni şifreler eşleşmiyor.")
        return attrs 

class UserSerializer(serializers.ModelSerializer):
    is_banned = serializers.ReadOnlyField()
    ban_reason = serializers.ReadOnlyField()
    ban_until = serializers.ReadOnlyField()
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_premium', 'is_premium_active', 
                 'email_verified', 'profile_picture', 'bio', 'phone_number', 'custom_username_color',
                 'card_number', 'card_issued_at', 'can_create_threads', 'is_secondhand_seller', 
                 'created_at', 'updated_at', 'is_banned', 'ban_reason', 'ban_until']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_banned', 'ban_reason', 'ban_until']

class PublicProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    is_following = serializers.SerializerMethodField()
    email = serializers.ReadOnlyField()
    is_premium_active = serializers.ReadOnlyField()
    email_verified = serializers.ReadOnlyField()
    card_issued_at = serializers.ReadOnlyField()
    can_create_threads = serializers.ReadOnlyField()
    updated_at = serializers.ReadOnlyField()
    thread_count = serializers.ReadOnlyField()
    is_banned = serializers.ReadOnlyField()
    ban_reason = serializers.ReadOnlyField()
    ban_until = serializers.ReadOnlyField()
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 'bio',
                 'phone_number', 'custom_username_color', 'card_number', 'card_issued_at',
                 'instagram', 'twitter', 'facebook', 'linkedin', 'website',
                 'is_premium', 'is_premium_active', 'email_verified', 'can_create_threads',
                 'is_secondhand_seller', 'followers_count', 'following_count',
                 'is_following', 'created_at', 'updated_at', 'thread_count',
                 'is_banned', 'ban_reason', 'ban_until']
        read_only_fields = ['id', 'email', 'is_premium', 'is_premium_active', 'email_verified',
                           'card_number', 'card_issued_at', 'can_create_threads', 'created_at', 'updated_at',
                           'is_banned', 'ban_reason', 'ban_until']
    
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.followers.all()
        return False

class FollowSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=['follow', 'unfollow']) 