from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import time

User = get_user_model()

class Event(models.Model):
    # Türkiye'nin 81 ili (alfabetik sıralı)
    CITIES = [
        ('adana', 'Adana'),
        ('adiyaman', 'Adıyaman'),
        ('afyonkarahisar', 'Afyonkarahisar'),
        ('agri', 'Ağrı'),
        ('aksaray', 'Aksaray'),
        ('amasya', 'Amasya'),
        ('ankara', 'Ankara'),
        ('antalya', 'Antalya'),
        ('ardahan', 'Ardahan'),
        ('artvin', 'Artvin'),
        ('aydin', 'Aydın'),
        ('balikesir', 'Balıkesir'),
        ('bartin', 'Bartın'),
        ('batman', 'Batman'),
        ('bayburt', 'Bayburt'),
        ('bilecik', 'Bilecik'),
        ('bingol', 'Bingöl'),
        ('bitlis', 'Bitlis'),
        ('bolu', 'Bolu'),
        ('burdur', 'Burdur'),
        ('bursa', 'Bursa'),
        ('canakkale', 'Çanakkale'),
        ('cankiri', 'Çankırı'),
        ('corum', 'Çorum'),
        ('denizli', 'Denizli'),
        ('diyarbakir', 'Diyarbakır'),
        ('duzce', 'Düzce'),
        ('edirne', 'Edirne'),
        ('elazig', 'Elazığ'),
        ('erzincan', 'Erzincan'),
        ('erzurum', 'Erzurum'),
        ('eskisehir', 'Eskişehir'),
        ('gaziantep', 'Gaziantep'),
        ('giresun', 'Giresun'),
        ('gumushane', 'Gümüşhane'),
        ('hakkari', 'Hakkari'),
        ('hatay', 'Hatay'),
        ('igdir', 'Iğdır'),
        ('isparta', 'Isparta'),
        ('istanbul', 'İstanbul'),
        ('izmir', 'İzmir'),
        ('kahramanmaras', 'Kahramanmaraş'),
        ('karabuk', 'Karabük'),
        ('karaman', 'Karaman'),
        ('kars', 'Kars'),
        ('kastamonu', 'Kastamonu'),
        ('kayseri', 'Kayseri'),
        ('kilis', 'Kilis'),
        ('kirikkale', 'Kırıkkale'),
        ('kirklareli', 'Kırklareli'),
        ('kirsehir', 'Kırşehir'),
        ('kocaeli', 'Kocaeli'),
        ('konya', 'Konya'),
        ('kutahya', 'Kütahya'),
        ('malatya', 'Malatya'),
        ('manisa', 'Manisa'),
        ('mardin', 'Mardin'),
        ('mersin', 'Mersin'),
        ('mugla', 'Muğla'),
        ('mus', 'Muş'),
        ('nevsehir', 'Nevşehir'),
        ('nigde', 'Niğde'),
        ('ordu', 'Ordu'),
        ('osmaniye', 'Osmaniye'),
        ('rize', 'Rize'),
        ('sakarya', 'Sakarya'),
        ('samsun', 'Samsun'),
        ('sanliurfa', 'Şanlıurfa'),
        ('siirt', 'Siirt'),
        ('sinop', 'Sinop'),
        ('sirnak', 'Şırnak'),
        ('sivas', 'Sivas'),
        ('tekirdag', 'Tekirdağ'),
        ('tokat', 'Tokat'),
        ('trabzon', 'Trabzon'),
        ('tunceli', 'Tunceli'),
        ('usak', 'Uşak'),
        ('van', 'Van'),
        ('yalova', 'Yalova'),
        ('yozgat', 'Yozgat'),
        ('zonguldak', 'Zonguldak'),
    ]
    
    name = models.CharField(max_length=255, default="Etkinlik")
    venue = models.CharField(max_length=255, default="Bilinmiyor")
    city = models.CharField(max_length=20, choices=CITIES, default='istanbul', verbose_name='İl')
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=time(0, 0))
    description = models.TextField(blank=True)
    ticket_price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    capacity = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)  # Etkinlik onay durumu
    organizer = models.CharField(max_length=255, blank=True, null=True, default="")

    def __str__(self):
        return f'{self.name} - {self.venue} ({self.get_city_display()})'

class Ticket(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    code = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return f'{self.user.username} - {self.event.name}'

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
