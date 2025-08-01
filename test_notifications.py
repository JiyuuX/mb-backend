#!/usr/bin/env python
import os
import sys
import django

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import CustomUser, Notification

def test_notification_system():
    print("Notification sistemi test ediliyor...")
    
    # Kullanıcıları al
    users = CustomUser.objects.all()
    if users.count() < 2:
        print("En az 2 kullanıcı gerekli!")
        return
    
    user1 = users[0]
    user2 = users[1]
    
    print(f"Test kullanıcıları: {user1.username} ve {user2.username}")
    
    # Mevcut bildirimleri temizle
    Notification.objects.filter(recipient=user2).delete()
    
    # Takip bildirimi oluştur
    notification = Notification.create_follow_notification(user1, user2)
    print(f"Bildirim oluşturuldu: {notification.title}")
    
    # Bildirimleri kontrol et
    notifications = Notification.objects.filter(recipient=user2)
    print(f"Kullanıcı {user2.username} için {notifications.count()} bildirim var")
    
    for notif in notifications:
        print(f"- {notif.title}: {notif.message}")
    
    # Okunmamış bildirim sayısını kontrol et
    unread_count = Notification.objects.filter(recipient=user2, is_read=False).count()
    print(f"Okunmamış bildirim sayısı: {unread_count}")
    
    # Tüm bildirimleri okundu olarak işaretle
    Notification.objects.filter(recipient=user2).update(is_read=True)
    unread_count_after = Notification.objects.filter(recipient=user2, is_read=False).count()
    print(f"Okundu işaretlendikten sonra okunmamış bildirim sayısı: {unread_count_after}")

if __name__ == "__main__":
    test_notification_system() 