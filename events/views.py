from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from .models import Event, Announcement
from .serializers import EventSerializer, AnnouncementSerializer

# Create your views here.

class UpcomingEventsListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return Event.objects.filter(is_approved=True, start_date__gte=now).order_by('start_date')

class ActiveAnnouncementsListView(generics.ListAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return Announcement.objects.filter(is_active=True, publish_date__lte=now).order_by('-publish_date')

class DashboardFeedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        events = Event.objects.filter(is_approved=True, start_date__gte=now).order_by('start_date')[:5]
        announcements = Announcement.objects.filter(is_active=True, publish_date__lte=now).order_by('-publish_date')[:5]
        # Reklamlar için ileride ekleme yapılabilir
        return Response({
            'upcoming_events': EventSerializer(events, many=True).data,
            'announcements': AnnouncementSerializer(announcements, many=True).data,
            'ads': []  # Şimdilik boş, ileride reklam modeli eklenebilir
        })
