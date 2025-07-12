from django.contrib import admin
from .models import News

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'priority', 'created_at')
    list_filter = ('is_active', 'priority', 'created_at')
    search_fields = ('title', 'content')
    list_editable = ('is_active', 'priority')
    ordering = ('-priority', '-created_at') 