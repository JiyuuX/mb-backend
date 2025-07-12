#!/usr/bin/env python
import os
import sys
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from news.models import News

def add_sample_news():
    """Örnek haberler ekle"""
    
    # Mevcut haberleri temizle
    News.objects.all().delete()
    print("Mevcut haberler silindi.")
    
    # Örnek haberler
    sample_news = [
        {
            'title': 'Kampüs festivali bu hafta sonu düzenleniyor',
            'content': 'Öğrenci kulüpleri tarafından organize edilen kampüs festivali bu hafta sonu gerçekleşecek.',
            'priority': 10,
        },
        {
            'title': 'Üniversitemizde yeni teknoloji laboratuvarı açıldı ve öğrenciler artık en son teknolojileri kullanabilecek, ayrıca yapay zeka ve robotik alanlarında da eğitim verilecek',
            'content': 'Mühendislik fakültesinde yeni teknoloji laboratuvarı öğrencilerin kullanımına açıldı. Laboratuvarda yapay zeka, robotik ve IoT teknolojileri bulunuyor.',
            'priority': 9,
        },
        {
            'title': 'Yeni dönem kayıtları başladı',
            'content': '2024-2025 akademik yılı kayıtları için öğrencilerin başvuruları alınmaya başlandı.',
            'priority': 8,
        },
    ]
    
    for news_data in sample_news:
        News.objects.create(
            title=news_data['title'],
            content=news_data['content'],
            priority=news_data['priority'],
            is_active=True
        )
    
    print(f"{len(sample_news)} adet örnek haber eklendi!")
    print("\nEklenen haberler:")
    for i, news in enumerate(News.objects.all(), 1):
        print(f"{i}. {news.title} (Öncelik: {news.priority})")
        print(f"   Uzunluk: {len(news.title)} karakter")
        print()

if __name__ == '__main__':
    add_sample_news() 