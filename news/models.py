from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Haber Başlığı")
    content = models.TextField(verbose_name="Haber İçeriği")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    priority = models.IntegerField(default=1, verbose_name="Öncelik (1-10)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        verbose_name = "Haber"
        verbose_name_plural = "Haberler"
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return self.title 