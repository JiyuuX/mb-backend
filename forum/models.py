from django.db import models
from django.conf import settings
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Thread(models.Model):
    title = models.CharField(max_length=200, verbose_name='Başlık')
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='threads', verbose_name='Oluşturan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False, verbose_name='Sabitlendi mi?')
    is_locked = models.BooleanField(default=False, verbose_name='Kilitli mi?')
    
    class Meta:
        verbose_name = 'Konu'
        verbose_name_plural = 'Konular'
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title

class Post(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='posts', verbose_name='Konu')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts', verbose_name='Yazar')
    content = models.TextField(verbose_name='İçerik')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False, verbose_name='Düzenlendi mi?')
    
    class Meta:
        verbose_name = 'Post'
        verbose_name_plural = 'Postlar'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.author} - {self.thread.title}"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name='Post')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Yazar')
    content = models.TextField(verbose_name='Yorum')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False, verbose_name='Düzenlendi mi?')
    
    class Meta:
        verbose_name = 'Yorum'
        verbose_name_plural = 'Yorumlar'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.author} - {self.post}"
