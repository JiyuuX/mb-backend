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
    
    CATEGORY_CHOICES = [
        ('genel', 'Genel'),
        ('muzik', 'Müzik'),
        ('oyun', 'Oyun'),
        ('film', 'Film'),
        ('spor', 'Spor'),
        ('teknoloji', 'Teknoloji'),
        ('espor', 'Espor'),
        ('finans', 'Finans&Kripto'),
        ('bilim', 'Bilim'),
        ('diger', 'Diğer'),
    ]
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES, default='genel', verbose_name='Kategori')
    likes = models.ManyToManyField(User, related_name='liked_threads', blank=True, verbose_name='Beğenenler')
    
    FORUM_TYPE_CHOICES = [
        ('genel', 'Genel'),
        ('itiraf', 'İtiraf'),
        ('yardim', 'Soru-Yardımlaşma'),
    ]
    forum_type = models.CharField(max_length=16, choices=FORUM_TYPE_CHOICES, default='genel', verbose_name='Forum Tipi')
    university = models.CharField(max_length=100, blank=True, null=True, verbose_name='Üniversite (Kampüs forumları için)')
    
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

class Report(models.Model):
    REPORT_CATEGORIES = [
        ('spam', 'Spam'),
        ('abuse', 'Hakaret/İftira'),
        ('misinfo', 'Yanlış Bilgi'),
        ('offtopic', 'Konu Dışı'),
        ('other', 'Diğer'),
    ]
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='reports', verbose_name='Raporlanan Konu', null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reports', verbose_name='Raporlanan Post', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reports', verbose_name='Raporlanan Yorum', null=True, blank=True)
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made', verbose_name='Raporlayan')
    category = models.CharField(max_length=32, choices=REPORT_CATEGORIES, verbose_name='Rapor Kategorisi')
    reason = models.TextField(blank=True, verbose_name='Açıklama (isteğe bağlı)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Rapor'
        verbose_name_plural = 'Raporlar'
        ordering = ['-created_at']

    def __str__(self):
        if self.thread:
            return f"Thread: {self.thread.title} - {self.category} by {self.reporter}"
        elif self.post:
            return f"Post: {self.post.id} - {self.category} by {self.reporter}"
        elif self.comment:
            return f"Comment: {self.comment.id} - {self.category} by {self.reporter}"
        return f"Report by {self.reporter}"

class DailyPopularThread(models.Model):
    """Günlük popüler thread takibi için model"""
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name='daily_popularity', verbose_name='Thread')
    date = models.DateField(auto_now_add=True, verbose_name='Tarih')
    like_count = models.IntegerField(default=0, verbose_name='Beğeni Sayısı')
    comment_count = models.IntegerField(default=0, verbose_name='Yorum Sayısı')
    score = models.IntegerField(default=0, verbose_name='Toplam Puan')
    forum_type = models.CharField(max_length=16, choices=Thread.FORUM_TYPE_CHOICES, verbose_name='Forum Tipi')
    university = models.CharField(max_length=100, blank=True, null=True, verbose_name='Üniversite')
    
    class Meta:
        verbose_name = 'Günlük Popüler Thread'
        verbose_name_plural = 'Günlük Popüler Threadler'
        unique_together = ['thread', 'date', 'forum_type', 'university']
        ordering = ['-date', '-score']
    
    def __str__(self):
        return f"{self.thread.title} - {self.date} - {self.forum_type}"
    
    def update_stats(self):
        """Thread'in güncel istatistiklerini güncelle"""
        self.like_count = self.thread.likes.count()
        self.comment_count = Comment.objects.filter(post__thread=self.thread).count()
        self.score = self.like_count * 2 + self.comment_count
        self.save()
