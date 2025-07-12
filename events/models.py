from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Event(models.Model):
    EVENT_TYPES = [
        ('academic', 'Akademik'),
        ('social', 'Sosyal'),
        ('sports', 'Spor'),
        ('cultural', 'Kültür'),
        ('career', 'Kariyer'),
        ('other', 'Diğer'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Başlık')
    description = models.TextField(verbose_name='Açıklama')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, verbose_name='Etkinlik Türü')
    
    # Tarih ve saat bilgileri
    start_date = models.DateTimeField(verbose_name='Başlangıç Tarihi')
    end_date = models.DateTimeField(verbose_name='Bitiş Tarihi')
    
    # Konum bilgileri
    location = models.CharField(max_length=200, verbose_name='Konum')
    location_details = models.TextField(blank=True, verbose_name='Konum Detayları')
    
    # Organizatör bilgileri
    organizer = models.CharField(max_length=100, verbose_name='Organizatör')
    contact_email = models.EmailField(blank=True, verbose_name='İletişim E-postası')
    contact_phone = models.CharField(max_length=15, blank=True, verbose_name='İletişim Telefonu')
    
    # Görsel ve medya
    image = models.ImageField(upload_to='events/', null=True, blank=True, verbose_name='Etkinlik Görseli')
    
    # Katılım bilgileri
    max_participants = models.PositiveIntegerField(null=True, blank=True, verbose_name='Maksimum Katılımcı')
    current_participants = models.PositiveIntegerField(default=0, verbose_name='Mevcut Katılımcı')
    
    # Durum ve onay
    is_approved = models.BooleanField(default=False, verbose_name='Onaylandı mı?')
    is_featured = models.BooleanField(default=False, verbose_name='Öne Çıkan')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Etkinlik'
        verbose_name_plural = 'Etkinlikler'
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_upcoming(self):
        """Yaklaşan etkinlik mi?"""
        return self.start_date > timezone.now()
    
    @property
    def is_ongoing(self):
        """Devam eden etkinlik mi?"""
        now = timezone.now()
        return self.start_date <= now <= self.end_date
    
    @property
    def is_full(self):
        """Katılımcı kontenjanı dolu mu?"""
        if self.max_participants is None:
            return False
        return self.current_participants >= self.max_participants

class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations', verbose_name='Etkinlik')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations', verbose_name='Kullanıcı')
    registration_date = models.DateTimeField(auto_now_add=True, verbose_name='Kayıt Tarihi')
    is_confirmed = models.BooleanField(default=True, verbose_name='Onaylandı mı?')
    
    class Meta:
        verbose_name = 'Etkinlik Kaydı'
        verbose_name_plural = 'Etkinlik Kayıtları'
        unique_together = ['event', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.title}"

class Announcement(models.Model):
    ANNOUNCEMENT_TYPES = [
        ('general', 'Genel'),
        ('academic', 'Akademik'),
        ('social', 'Sosyal'),
        ('emergency', 'Acil'),
        ('reminder', 'Hatırlatma'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Başlık')
    content = models.TextField(verbose_name='İçerik')
    announcement_type = models.CharField(max_length=20, choices=ANNOUNCEMENT_TYPES, verbose_name='Duyuru Türü')
    
    # Görsel
    image = models.ImageField(upload_to='announcements/', null=True, blank=True, verbose_name='Duyuru Görseli')
    
    # Durum
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')
    is_featured = models.BooleanField(default=False, verbose_name='Öne Çıkan')
    
    # Tarih bilgileri
    publish_date = models.DateTimeField(default=timezone.now, verbose_name='Yayın Tarihi')
    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name='Bitiş Tarihi')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Duyuru'
        verbose_name_plural = 'Duyurular'
        ordering = ['-publish_date']
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        """Duyuru süresi dolmuş mu?"""
        if self.expiry_date is None:
            return False
        return timezone.now() > self.expiry_date
