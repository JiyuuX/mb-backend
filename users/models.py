from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    # Premium üyelik durumu
    is_premium = models.BooleanField(default=False)
    premium_expires_at = models.DateTimeField(null=True, blank=True)
    
    # Email aktivasyonu
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Profil bilgileri
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    
    # Premium özellikler
    custom_username_color = models.CharField(max_length=7, default='#000000')  # Hex color code
    
    # Kart bilgileri (premium kullanıcılar için)
    card_number = models.CharField(max_length=20, blank=True)
    card_issued_at = models.DateTimeField(null=True, blank=True)
    
    # Forum yetkileri
    can_create_threads = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
    
    def __str__(self):
        return self.username
    
    @property
    def is_premium_active(self):
        """Premium üyeliğin aktif olup olmadığını kontrol eder"""
        if not self.is_premium:
            return False
        if self.premium_expires_at and self.premium_expires_at < timezone.now():
            self.is_premium = False
            self.save()
            return False
        return True
    
    def activate_premium(self, duration_days=30):
        """Premium üyeliği aktifleştirir"""
        from django.utils import timezone
        self.is_premium = True
        self.premium_expires_at = timezone.now() + timezone.timedelta(days=duration_days)
        self.can_create_threads = True
        self.save()
    
    def generate_card_number(self):
        """Kart numarası oluşturur"""
        import random
        card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
        self.card_number = card_number
        self.card_issued_at = timezone.now()
        self.save()
        return card_number
