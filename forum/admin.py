from django.contrib import admin
from .models import Thread, Post, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('author', 'content', 'is_edited', 'created_at', 'updated_at')

class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    fields = ('author', 'content', 'is_edited', 'created_at', 'updated_at')

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'category', 'is_pinned', 'is_locked', 'created_at', 'post_count', 'like_count')
    list_filter = ('category', 'is_pinned', 'is_locked', 'created_at')
    search_fields = ('title', 'creator__username', 'creator__email')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_pinned', 'is_locked')
    inlines = [PostInline]
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'creator', 'category')
        }),
        ('Durum', {
            'fields': ('is_pinned', 'is_locked')
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Beğeniler', {
            'fields': ('likes',),
            'classes': ('collapse',)
        }),
    )
    
    def post_count(self, obj):
        return obj.posts.count()
    post_count.short_description = 'Post Sayısı'
    
    def like_count(self, obj):
        return obj.likes.count()
    like_count.short_description = 'Beğeni Sayısı'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'thread_title', 'content_preview', 'is_edited', 'created_at', 'comment_count')
    list_filter = ('is_edited', 'created_at', 'thread__category')
    search_fields = ('content', 'author__username', 'thread__title')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_edited',)
    inlines = [CommentInline]
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('thread', 'author', 'content')
        }),
        ('Durum', {
            'fields': ('is_edited',)
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def thread_title(self, obj):
        return obj.thread.title
    thread_title.short_description = 'Konu Başlığı'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'İçerik Önizleme'
    
    def comment_count(self, obj):
        return obj.comments.count()
    comment_count.short_description = 'Yorum Sayısı'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post_preview', 'content_preview', 'is_edited', 'created_at')
    list_filter = ('is_edited', 'created_at')
    search_fields = ('content', 'author__username', 'post__content')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_edited',)
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('post', 'author', 'content')
        }),
        ('Durum', {
            'fields': ('is_edited',)
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def post_preview(self, obj):
        return f"{obj.post.author} - {obj.post.content[:50]}..."
    post_preview.short_description = 'Post'
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Yorum Önizleme'
