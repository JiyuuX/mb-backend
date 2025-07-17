from django.db import models
from django.utils import timezone

class Advertisement(models.Model):
    title = models.CharField(max_length=200, verbose_name="Reklam Başlığı")
    description = models.TextField(verbose_name="Reklam Açıklaması", blank=True)
    company_name = models.CharField(max_length=100, verbose_name="Şirket Adı")
    gif_file = models.FileField(upload_to='ads/gifs/', verbose_name="Reklam GIF'i", blank=True, null=True)
    image_file = models.ImageField(upload_to='ads/images/', verbose_name="Reklam Görseli", blank=True, null=True)
    video_file = models.FileField(upload_to='ads/videos/', verbose_name="Reklam Videosu (MP4)", blank=True, null=True)
    link_url = models.URLField(verbose_name="Reklam Linki", blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    priority = models.IntegerField(default=1, verbose_name="Öncelik (1-10)")
    start_date = models.DateTimeField(verbose_name="Başlangıç Tarihi", default=timezone.now)
    end_date = models.DateTimeField(verbose_name="Bitiş Tarihi", null=True, blank=True)
    click_count = models.IntegerField(default=0, verbose_name="Tıklama Sayısı")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Reklam"
        verbose_name_plural = "Reklamlar"
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.company_name} - {self.title}"
    
    def is_currently_active(self):
        """Reklamın şu anda aktif olup olmadığını kontrol et"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True 