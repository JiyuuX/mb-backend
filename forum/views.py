from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from .models import Thread, Post, Comment, Report
from .serializers import ThreadSerializer, PostSerializer, CommentSerializer, ReportSerializer
from rest_framework.permissions import IsAuthenticated
from datetime import timedelta
from django.utils import timezone
from users.permissions import IsNotBanned
from rest_framework.decorators import api_view

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
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]

    def perform_create(self, serializer):
        if not self.request.user.is_premium:
            raise PermissionDenied('Sadece premium kullanıcılar thread oluşturabilir.')
        serializer.save(creator=self.request.user)

class ThreadDetailView(generics.RetrieveAPIView):
    queryset = Thread.objects.all()
    serializer_class = ThreadSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]

class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]

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
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]

class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
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
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]

class ThreadStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
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

# Hot Topics API
class HotTopicsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]

    def get(self, request):
        since = timezone.now() - timedelta(hours=24)
        threads = Thread.objects.filter(created_at__gte=since)
        thread_stats = []
        for thread in threads:
            like_count = thread.likes.count()
            comment_count = Comment.objects.filter(post__thread=thread).count()
            # Filtre: Hem beğeni hem yorum sıfırsa ekleme
            if like_count == 0 and comment_count == 0:
                continue
            score = like_count * 2 + comment_count
            thread_stats.append({
                'thread': ThreadSerializer(thread, context={'request': request}).data,
                'like_count': like_count,
                'comment_count': comment_count,
                'score': score,
            })
        hot = sorted(thread_stats, key=lambda x: x['score'], reverse=True)[:10]
        return Response(hot)

# Campus Daily Popular Threads API
class CampusDailyPopularView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]

    def get(self, request):
        university = request.GET.get('university')
        forum_type = request.GET.get('forum_type', 'genel')
        
        if not university:
            return Response({'success': False, 'message': 'university parametresi gerekli.'}, status=400)
        
        from .models import DailyPopularThread
        from datetime import date
        
        today = date.today()
        
        # Bugün için popüler thread'i al
        daily_popular = DailyPopularThread.objects.filter(
            date=today,
            forum_type=forum_type,
            university=university
        ).first()
        
        if daily_popular:
            # İstatistikleri güncelle
            daily_popular.update_stats()
            
            return Response({
                'success': True,
                'thread': ThreadSerializer(daily_popular.thread, context={'request': request}).data,
                'like_count': daily_popular.like_count,
                'comment_count': daily_popular.comment_count,
                'score': daily_popular.score,
                'date': daily_popular.date,
            })
        else:
            # Bugün için popüler thread yoksa, son 24 saatteki en popüler thread'i bul
            since = timezone.now() - timedelta(hours=24)
            threads = Thread.objects.filter(
                university=university,
                forum_type=forum_type,
                created_at__gte=since
            )
            
            thread_stats = []
            for thread in threads:
                like_count = thread.likes.count()
                comment_count = Comment.objects.filter(post__thread=thread).count()
                if like_count == 0 and comment_count == 0:
                    continue
                score = like_count * 2 + comment_count
                thread_stats.append({
                    'thread': thread,
                    'like_count': like_count,
                    'comment_count': comment_count,
                    'score': score,
                })
            
            if thread_stats:
                # En popüler thread'i seç
                most_popular = max(thread_stats, key=lambda x: x['score'])
                
                # DailyPopularThread kaydı oluştur
                daily_popular = DailyPopularThread.objects.create(
                    thread=most_popular['thread'],
                    forum_type=forum_type,
                    university=university,
                    like_count=most_popular['like_count'],
                    comment_count=most_popular['comment_count'],
                    score=most_popular['score']
                )
                
                return Response({
                    'success': True,
                    'thread': ThreadSerializer(most_popular['thread'], context={'request': request}).data,
                    'like_count': most_popular['like_count'],
                    'comment_count': most_popular['comment_count'],
                    'score': most_popular['score'],
                    'date': daily_popular.date,
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Bu forum tipi için popüler thread bulunamadı.'
                }, status=404)

# Thread Like Toggle View'ını güncelle - günlük popülerlik takibi için
class ThreadLikeToggleView(APIView):
    permission_classes = [IsAuthenticated, IsNotBanned]

    def post(self, request, thread_id):
        thread = get_object_or_404(Thread, id=thread_id)
        user = request.user
        if thread.likes.filter(id=user.id).exists():
            thread.likes.remove(user)
            liked = False
        else:
            thread.likes.add(user)
            liked = True
        
        # Günlük popülerlik takibini güncelle
        from .models import DailyPopularThread
        from datetime import date
        
        today = date.today()
        
        # Genel forum için günlük popülerlik takibi
        if thread.forum_type == 'genel' and not thread.university:
            daily_popular, created = DailyPopularThread.objects.get_or_create(
                thread=thread,
                date=today,
                forum_type='genel',
                university=None,
                defaults={
                    'like_count': thread.likes.count(),
                    'comment_count': Comment.objects.filter(post__thread=thread).count(),
                    'score': thread.likes.count() * 2 + Comment.objects.filter(post__thread=thread).count()
                }
            )
            if not created:
                daily_popular.update_stats()
        
        # Kampüs forumu için günlük popülerlik takibi
        elif thread.university:
            daily_popular, created = DailyPopularThread.objects.get_or_create(
                thread=thread,
                date=today,
                forum_type=thread.forum_type,
                university=thread.university,
                defaults={
                    'like_count': thread.likes.count(),
                    'comment_count': Comment.objects.filter(post__thread=thread).count(),
                    'score': thread.likes.count() * 2 + Comment.objects.filter(post__thread=thread).count()
                }
            )
            if not created:
                daily_popular.update_stats()
        
        return Response({
            'liked': liked,
            'likes_count': thread.likes.count(),
        })

class ReportCreateView(APIView):
    permission_classes = [IsAuthenticated, IsNotBanned]

    def post(self, request, thread_id=None, post_id=None, comment_id=None):
        user = request.user
        if thread_id:
            thread = get_object_or_404(Thread, id=thread_id)
            # Kendi threadini report edemez
            if thread.creator == user:
                return Response({'success': False, 'message': 'Kendi oluşturduğun threadi report edemezsin.'}, status=400)
            # Aynı kullanıcı aynı thread'i 30 dakika içinde tekrar reportlayamaz
            thirty_mins_ago = timezone.now() - timedelta(minutes=30)
            if Report.objects.filter(thread=thread, reporter=user, created_at__gte=thirty_mins_ago).exists():
                return Response({'success': False, 'message': 'Bu threadi zaten yakın zamanda reportladınız.'}, status=400)
            serializer = ReportSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(thread=thread, reporter=user)
                # Otomatik kaldırma kontrolü
                recent_reports = Report.objects.filter(thread=thread, created_at__gte=thirty_mins_ago).count()
                if recent_reports >= 10:
                    thread.is_locked = True
                    thread.save()
                return Response({'success': True, 'message': 'Raporunuz alındı.'}, status=201)
            return Response({'success': False, 'message': serializer.errors}, status=400)
        elif post_id:
            from .models import Post
            post = get_object_or_404(Post, id=post_id)
            if post.author == user:
                return Response({'success': False, 'message': 'Kendi postunu report edemezsin.'}, status=400)
            thirty_mins_ago = timezone.now() - timedelta(minutes=30)
            if Report.objects.filter(post=post, reporter=user, created_at__gte=thirty_mins_ago).exists():
                return Response({'success': False, 'message': 'Bu postu zaten yakın zamanda reportladınız.'}, status=400)
            serializer = ReportSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(post=post, reporter=user)
                recent_reports = Report.objects.filter(post=post, created_at__gte=thirty_mins_ago).count()
                if recent_reports >= 10:
                    post.is_edited = True  # veya post silinebilir
                    post.save()
                return Response({'success': True, 'message': 'Post raporlandı.'}, status=201)
            return Response({'success': False, 'message': serializer.errors}, status=400)
        elif comment_id:
            from .models import Comment
            comment = get_object_or_404(Comment, id=comment_id)
            # Kendi yorumunu report edemez
            if comment.author == user:
                return Response({'success': False, 'message': 'Kendi yorumunu report edemezsin.'}, status=400)
            thirty_mins_ago = timezone.now() - timedelta(minutes=30)
            if Report.objects.filter(comment=comment, reporter=user, created_at__gte=thirty_mins_ago).exists():
                return Response({'success': False, 'message': 'Bu yorumu zaten yakın zamanda reportladınız.'}, status=400)
            serializer = ReportSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(comment=comment, reporter=user)
                # Otomatik kaldırma kontrolü
                recent_reports = Report.objects.filter(comment=comment, created_at__gte=thirty_mins_ago).count()
                if recent_reports >= 10:
                    comment.is_edited = True  # veya comment silinebilir
                    comment.save()
                return Response({'success': True, 'message': 'Yorum raporlandı.'}, status=201)
            return Response({'success': False, 'message': serializer.errors}, status=400)
        else:
            return Response({'success': False, 'message': 'Geçersiz istek.'}, status=400)

@api_view(['GET'])
def campus_forum_threads(request):
    university = request.GET.get('university')
    forum_type = request.GET.get('forum_type')
    if not university or not forum_type:
        return Response({'success': False, 'message': 'university ve forum_type parametreleri gerekli.'}, status=400)
    threads = Thread.objects.filter(university=university, forum_type=forum_type).order_by('-is_pinned', '-created_at')
    serializer = ThreadSerializer(threads, many=True, context={'request': request})
    # Ekstra: like_count ve comment_count ekle
    thread_data = []
    for thread, data in zip(threads, serializer.data):
        like_count = thread.likes.count()
        comment_count = Comment.objects.filter(post__thread=thread).count()
        data = dict(data)
        data['like_count'] = like_count
        data['comment_count'] = comment_count
        thread_data.append(data)
    return Response({'success': True, 'threads': thread_data})
