from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import News
from .serializers import NewsSerializer

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