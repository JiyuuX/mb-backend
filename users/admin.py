from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_premium', 'email_verified', 'is_staff', 'is_active')
    list_filter = ('is_premium', 'email_verified', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email', 'profile_picture', 'bio', 'phone_number')}),
        ('Premium Özellikler', {'fields': ('is_premium', 'premium_expires_at', 'custom_username_color', 'card_number', 'card_issued_at')}),
        ('Email Aktivasyonu', {'fields': ('email_verified', 'email_verification_token', 'email_verification_sent_at')}),
        ('Forum Yetkileri', {'fields': ('can_create_threads',)}),
        ('İzinler', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Önemli Tarihler', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
