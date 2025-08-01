from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserRegistrationView, UserLoginView, EmailVerificationView, 
    ResendVerificationEmailView, UserProfileView, UserUpdateView, PasswordChangeView, 
    LogoutView, ActivatePremiumView, PublicProfileView, FollowUserView, 
    UserFollowersView, UserFollowingView, UpdateUsernameColorView, UniversityListView, 
    RequestNameChangeView, VerifyNameChangeView, DeleteAccountView, popular_users,
    NotificationListView, MarkNotificationsAsReadView, UnreadNotificationCountView
)

router = DefaultRouter()
router.register(r'actions', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('update/', UserUpdateView.as_view(), name='update'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('activate-premium/', ActivatePremiumView.as_view(), name='activate-premium'),
    path('update-username-color/', UpdateUsernameColorView.as_view(), name='update-username-color'),
    path('request-name-change/', RequestNameChangeView.as_view(), name='request-name-change'),
    path('verify-name-change/', VerifyNameChangeView.as_view(), name='verify-name-change'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),
    # Public profile and follow system
    path('public/<str:username>/', PublicProfileView.as_view(), name='public-profile'),
    path('follow/', FollowUserView.as_view(), name='follow-user'),
    path('followers/<str:username>/', UserFollowersView.as_view(), name='user-followers'),
    path('following/<str:username>/', UserFollowingView.as_view(), name='user-following'),
    path('universities/', UniversityListView.as_view(), name='university-list'),
    path('popular-users/', popular_users, name='popular-users'),
    # Notification system
    path('notifications/', NotificationListView.as_view(), name='notifications'),
    path('notifications/mark-read/', MarkNotificationsAsReadView.as_view(), name='mark-notifications-read'),
    path('notifications/unread-count/', UnreadNotificationCountView.as_view(), name='unread-notification-count'),
] 