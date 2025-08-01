from django.contrib import admin
from .models import Thread, Post, Comment, Report, DailyPopularThread

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

class ReportInline(admin.TabularInline):
    model = Report
    extra = 0
    readonly_fields = ('report_type', 'target_info', 'reporter_username', 'category', 'reason', 'created_at')
    fields = ('report_type', 'target_info', 'reporter_username', 'category', 'reason', 'created_at')
    can_delete = False
    show_change_link = True

    def report_type(self, obj):
        if obj.thread:
            return 'Thread'
        elif obj.comment:
            return 'Comment'
        return '-'
    report_type.short_description = 'Tip'

    def target_info(self, obj):
        if obj.thread:
            return f"{obj.thread.title} (Sahibi: {obj.thread.creator})"
        elif obj.post:
            return f"Post: {obj.post.content[:40]}... (Yazar: {obj.post.author})"
        elif obj.comment:
            return f"Yorum: {obj.comment.content[:40]}... (Yazar: {obj.comment.author})"
        return '-'
    target_info.short_description = 'Raporlanan'

    def reporter_username(self, obj):
        return obj.reporter.username
    reporter_username.short_description = 'Raporlayan'

@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'category', 'is_pinned', 'is_locked', 'created_at', 'post_count', 'like_count', 'report_count')
    list_filter = ('category', 'is_pinned', 'is_locked', 'created_at')
    search_fields = ('title', 'creator__username', 'creator__email')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('is_pinned', 'is_locked')
    inlines = [PostInline, ReportInline]
    
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

    def report_count(self, obj):
        return obj.reports.count()
    report_count.short_description = 'Rapor Sayısı'

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

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_type', 'target_info', 'reporter_username', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('thread__title', 'comment__content', 'reporter__username', 'reason')
    readonly_fields = ('report_type', 'target_info', 'reporter_username', 'category', 'reason', 'created_at')
    fields = ('report_type', 'target_info', 'reporter_username', 'category', 'reason', 'created_at')

    def report_type(self, obj):
        if obj.thread:
            return 'Thread'
        elif obj.comment:
            return 'Comment'
        return '-'
    report_type.short_description = 'Tip'

    def target_info(self, obj):
        if obj.thread:
            return f"{obj.thread.title} (Sahibi: {obj.thread.creator})"
        elif obj.post:
            return f"Post: {obj.post.content[:40]}... (Yazar: {obj.post.author})"
        elif obj.comment:
            return f"Yorum: {obj.comment.content[:40]}... (Yazar: {obj.comment.author})"
        return '-'
    target_info.short_description = 'Raporlanan'

    def reporter_username(self, obj):
        return obj.reporter.username
    reporter_username.short_description = 'Raporlayan'

@admin.register(DailyPopularThread)
class DailyPopularThreadAdmin(admin.ModelAdmin):
    list_display = ('thread_title', 'forum_type', 'university', 'date', 'like_count', 'comment_count', 'score')
    list_filter = ('forum_type', 'university', 'date')
    search_fields = ('thread__title', 'university')
    readonly_fields = ('thread', 'date', 'like_count', 'comment_count', 'score', 'forum_type', 'university')
    ordering = ('-date', '-score')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('thread', 'forum_type', 'university')
        }),
        ('Tarih', {
            'fields': ('date',)
        }),
        ('İstatistikler', {
            'fields': ('like_count', 'comment_count', 'score')
        }),
    )
    
    def thread_title(self, obj):
        return obj.thread.title
    thread_title.short_description = 'Thread Başlığı'
    
    def has_add_permission(self, request):
        return False  # Manuel eklemeyi engelle
    
    def has_change_permission(self, request, obj=None):
        return False  # Düzenlemeyi engelle
