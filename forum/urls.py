from django.urls import path
from .views import (
    ThreadListCreateView, ThreadDetailView, PostListCreateView, 
    PostDetailView, CommentListCreateView, CommentDetailView, ThreadStatsView
)

urlpatterns = [
    path('threads/', ThreadListCreateView.as_view(), name='thread-list-create'),
    path('threads/<int:pk>/', ThreadDetailView.as_view(), name='thread-detail'),
    path('threads/<int:thread_id>/posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('threads/<int:thread_id>/stats/', ThreadStatsView.as_view(), name='thread-stats'),
] 