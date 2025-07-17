from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Advertisement
from .serializers import AdvertisementSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsNotBanned

@api_view(['GET'])
def get_active_ads(request):
    """Aktif reklamları getir"""
    try:
        # Şu anda aktif olan reklamları al
        ads = Advertisement.objects.filter(is_active=True).order_by('-priority', '-created_at')
        
        # Tarih kontrolü yap
        active_ads = []
        for ad in ads:
            if ad.is_currently_active():
                active_ads.append(ad)
        
        serializer = AdvertisementSerializer(active_ads, many=True, context={'request': request})
        return Response({
            'success': True,
            'ads': serializer.data
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsNotBanned])
def ad_click(request, ad_id):
    """Reklam tıklama sayısını artır"""
    try:
        ad = Advertisement.objects.get(id=ad_id)
        ad.click_count += 1
        ad.save()
        return Response({
            'success': True,
            'message': 'Tıklama sayısı güncellendi'
        })
    except Advertisement.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Reklam bulunamadı'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 