from django.urls import path
from .views import (
    UserRegistrationView, UserLoginView, EmailVerificationView,
    ResendVerificationEmailView, UserProfileView, UserUpdateView,
    PasswordChangeView, LogoutView, ActivatePremiumView
)

app_name = 'users'

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-email/<uuid:token>/', EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend-verification'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('update/', UserUpdateView.as_view(), name='update'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('activate-premium/', ActivatePremiumView.as_view(), name='activate-premium'),
] 