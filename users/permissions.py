from rest_framework import permissions
from django.utils import timezone

class IsNotBanned(permissions.BasePermission):
    """
    Kullanıcı banlıysa veya ban süresi dolmamışsa erişimi engeller.
    """
    message = {
        'banli': True,
        'ban_sebebi': None,
        'ban_suresiz': None,
        'ban_bitis': None,
        'kalan_sure': None,
        'mesaj': 'Hesabınız banlanmıştır.'
    }

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return True  # Auth gerektirmeyenler için engelleme yok
        if getattr(user, 'is_banned', False):
            now = timezone.now()
            if user.ban_until is None or (user.ban_until and user.ban_until > now):
                kalan_sure = None
                if user.ban_until:
                    kalan_sure = user.ban_until - now
                self.message = {
                    'banli': True,
                    'ban_sebebi': user.ban_reason,
                    'ban_suresiz': user.ban_until is None,
                    'ban_bitis': user.ban_until,
                    'kalan_sure': kalan_sure.total_seconds() if kalan_sure else None,
                    'mesaj': f"Hesabınız {'süresiz' if user.ban_until is None else 'süreli'} olarak banlanmıştır. {f'Kalan süre: {kalan_sure}' if kalan_sure else ''}"
                }
                return False
        return True 