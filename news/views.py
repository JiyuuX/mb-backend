from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import News, CampusNews, DailySuggestion
from .serializers import NewsSerializer, CampusNewsSerializer, DailySuggestionSerializer

@api_view(['GET'])
def get_active_news(request):
    """Aktif haberleri getir - ticker için"""
    try:
        news = News.objects.filter(is_active=True).order_by('-priority', '-created_at')
        serializer = NewsSerializer(news, many=True)
        return Response({
            'success': True,
            'news': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_campus_news(request):
    """Belirli bir üniversiteye ait aktif kampüs haberlerini getirir."""
    university = request.GET.get('university')
    if not university:
        return Response({'success': False, 'message': 'university parametresi gerekli.'}, status=400)
    news = CampusNews.objects.filter(is_active=True, university=university).order_by('-created_at')
    serializer = CampusNewsSerializer(news, many=True)
    return Response({'success': True, 'news': serializer.data})

@api_view(['GET'])
def get_daily_suggestion(request):
    suggestion = DailySuggestion.objects.filter(is_active=True).order_by('-created_at').first()
    if suggestion:
        serializer = DailySuggestionSerializer(suggestion)
        return Response({'success': True, 'suggestion': serializer.data})
    return Response({'success': False, 'message': 'Günün önerisi bulunamadı.'}, status=404) 