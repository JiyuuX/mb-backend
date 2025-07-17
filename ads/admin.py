from django.contrib import admin
from .models import Advertisement

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'is_active', 'priority', 'start_date', 'end_date', 'click_count')
    list_filter = ('is_active', 'priority', 'start_date', 'end_date', 'company_name')
    search_fields = ('title', 'company_name', 'description')
    list_editable = ('is_active', 'priority')
    readonly_fields = ('click_count', 'created_at', 'updated_at')
    ordering = ('-priority', '-created_at')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'description', 'company_name')
        }),
        ('Medya', {
            'fields': ('gif_file', 'image_file', 'video_file', 'link_url')
        }),
        ('Durum', {
            'fields': ('is_active', 'priority', 'start_date', 'end_date')
        }),
        ('İstatistikler', {
            'fields': ('click_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    ) 