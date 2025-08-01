#!/usr/bin/env python
import os
import sys
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q

def test_popular_users_system():
    print("Popüler kullanıcılar sistemi test ediliyor...")
    
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
    
    print(f"Top {popular_users.count()} popüler kullanıcı:")
    print("-" * 50)
    
    for i, user in enumerate(popular_users, 1):
        print(f"#{i} - {user.username}")
        print(f"  Puan: {user.popularity}")
        print(f"  Thread Beğenileri: {user.thread_likes}")
        print(f"  Yeni Takipçiler: {user.new_followers}")
        print(f"  Toplam Takipçi: {user.followers.count()}")
        print(f"  Premium: {'Evet' if user.is_premium else 'Hayır'}")
        print("-" * 30)
    
    if popular_users.count() == 0:
        print("Henüz popüler kullanıcı yok. Kullanıcıların thread oluşturması ve beğeni alması gerekiyor.")

if __name__ == "__main__":
    test_popular_users_system() 