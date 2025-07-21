from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserRegistrationView, UserLoginView, EmailVerificationView, 
    ResendVerificationEmailView, UserProfileView, UserUpdateView, PasswordChangeView, 
    LogoutView, ActivatePremiumView, PublicProfileView, FollowUserView, 
    UserFollowersView, UserFollowingView, UpdateUsernameColorView
)

router = DefaultRouter()
router.register(r'actions', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/<uuid:token>/', EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('update/', UserUpdateView.as_view(), name='update'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('activate-premium/', ActivatePremiumView.as_view(), name='activate-premium'),
    path('update-username-color/', UpdateUsernameColorView.as_view(), name='update-username-color'),
    # Public profile and follow system
    path('public/<str:username>/', PublicProfileView.as_view(), name='public-profile'),
    path('follow/', FollowUserView.as_view(), name='follow-user'),
    path('followers/<str:username>/', UserFollowersView.as_view(), name='user-followers'),
    path('following/<str:username>/', UserFollowingView.as_view(), name='user-following'),
] 