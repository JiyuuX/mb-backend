from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import Thread, Post, Comment
from .serializers import ThreadSerializer, PostSerializer, CommentSerializer

# Create your views here.

class CommentPagination(PageNumberPagination):
    page_size = 5  # Sayfa başına 5 yorum
    page_size_query_param = 'page_size'
    max_page_size = 20

class IsPremiumUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_premium

class ThreadListCreateView(generics.ListCreateAPIView):
    queryset = Thread.objects.all().order_by('-is_pinned', '-created_at')
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if not self.request.user.is_premium:
            raise PermissionDenied('Sadece premium kullanıcılar thread oluşturabilir.')
        serializer.save(creator=self.request.user)

class ThreadDetailView(generics.RetrieveAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        thread_id = self.kwargs.get('thread_id')
        return Post.objects.filter(thread_id=thread_id).order_by('created_at')

    def perform_create(self, serializer):
        thread_id = self.kwargs.get('thread_id')
        thread = get_object_or_404(Thread, id=thread_id)
        serializer.save(author=self.request.user, thread=thread)

class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CommentPagination

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id).order_by('created_at')

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)

class CommentDetailView(generics.RetrieveAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

class ThreadStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, thread_id):
        thread = get_object_or_404(Thread, id=thread_id)
        posts_count = Post.objects.filter(thread=thread).count()
        comments_count = Comment.objects.filter(post__thread=thread).count()
        
        return Response({
            'thread_id': thread_id,
            'posts_count': posts_count,
            'comments_count': comments_count,
            'created_at': thread.created_at,
            'creator': {
                'username': thread.creator.username,
                'is_premium': thread.creator.is_premium,
            }
        })
