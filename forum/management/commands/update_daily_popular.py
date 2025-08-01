from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from forum.models import Thread, DailyPopularThread


class Command(BaseCommand):
    help = 'Günlük popüler thread\'leri günceller'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Mevcut günlük popüler thread\'leri zorla güncelle',
        )

    def handle(self, *args, **options):
        today = timezone.now().date()
        force_update = options['force']
        
        self.stdout.write(f"Günlük popüler thread güncelleme başladı - {today}")
        
        # Genel forum için günlük popüler thread
        self.update_daily_popular_for_forum('genel', None)
        
        # Kampüs forumları için günlük popüler thread
        universities = Thread.objects.filter(
            university__isnull=False
        ).values_list('university', flat=True).distinct()
        
        for university in universities:
            for forum_type in ['itiraf', 'yardim']:
                self.update_daily_popular_for_forum(forum_type, university)
        
        self.stdout.write(
            self.style.SUCCESS('Günlük popüler thread güncelleme tamamlandı')
        )

    def update_daily_popular_for_forum(self, forum_type, university):
        today = timezone.now().date()
        
        # Bugün için mevcut günlük popüler thread'i kontrol et
        existing_daily = DailyPopularThread.objects.filter(
            date=today,
            forum_type=forum_type,
            university=university
        ).first()
        
        if existing_daily and not self.options.get('force'):
            self.stdout.write(
                f"{forum_type} forumu ({university or 'genel'}) için günlük popüler thread zaten mevcut"
            )
            return
        
        # Son 24 saatteki thread'leri al
        since = timezone.now() - timedelta(hours=24)
        threads = Thread.objects.filter(
            forum_type=forum_type,
            created_at__gte=since
        )
        
        if university:
            threads = threads.filter(university=university)
        else:
            threads = threads.filter(university__isnull=True)
        
        if not threads.exists():
            self.stdout.write(
                f"{forum_type} forumu ({university or 'genel'}) için thread bulunamadı"
            )
            return
        
        # En popüler thread'i bul
        thread_stats = []
        for thread in threads:
            like_count = thread.likes.count()
            comment_count = thread.posts.count()  # Basit yorum sayısı
            if like_count == 0 and comment_count == 0:
                continue
            score = like_count * 2 + comment_count
            thread_stats.append({
                'thread': thread,
                'like_count': like_count,
                'comment_count': comment_count,
                'score': score,
            })
        
        if not thread_stats:
            self.stdout.write(
                f"{forum_type} forumu ({university or 'genel'}) için popüler thread bulunamadı"
            )
            return
        
        # En popüler thread'i seç
        most_popular = max(thread_stats, key=lambda x: x['score'])
        
        # Günlük popüler thread kaydını oluştur veya güncelle
        daily_popular, created = DailyPopularThread.objects.get_or_create(
            thread=most_popular['thread'],
            date=today,
            forum_type=forum_type,
            university=university,
            defaults={
                'like_count': most_popular['like_count'],
                'comment_count': most_popular['comment_count'],
                'score': most_popular['score']
            }
        )
        
        if not created:
            # Mevcut kaydı güncelle
            daily_popular.like_count = most_popular['like_count']
            daily_popular.comment_count = most_popular['comment_count']
            daily_popular.score = most_popular['score']
            daily_popular.save()
        
        action = "oluşturuldu" if created else "güncellendi"
        self.stdout.write(
            f"{forum_type} forumu ({university or 'genel'}) için günlük popüler thread {action}: "
            f"{most_popular['thread'].title} (Puan: {most_popular['score']})"
        ) 