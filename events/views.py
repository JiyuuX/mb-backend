from django.shortcuts import render
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.utils import timezone
from .models import Event, Announcement, Ticket
from .serializers import EventSerializer, AnnouncementSerializer, TicketSerializer
from django.utils.crypto import get_random_string
from users.permissions import IsNotBanned

# Create your views here.

class UpcomingEventsListView(generics.ListAPIView):
    serializer_class = EventSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now().date()
        three_days_later = now + timezone.timedelta(days=3)
        # Dashboard'la aynı mantık: bugünden 3 güne kadar olan etkinlikler
        queryset = Event.objects.filter(is_approved=True, date__gte=now, date__lte=three_days_later).order_by('date')
        
        # Şehir filtresi ekle
        city = self.request.query_params.get('city')
        if city:
            queryset = queryset.filter(city__iexact=city)
        
        return queryset

class ActiveAnnouncementsListView(generics.ListAPIView):
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        now = timezone.now()
        return Announcement.objects.filter(is_active=True, publish_date__lte=now).order_by('-publish_date')

class DashboardFeedView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]

    def get(self, request):
        now = timezone.now().date()
        three_days_later = now + timezone.timedelta(days=3)
        city = request.query_params.get('city')
        events_qs = Event.objects.filter(is_approved=True, date__gte=now, date__lte=three_days_later)
        if city:
            events_qs = events_qs.filter(city__iexact=city)
        events = events_qs.order_by('date')[:5]
        announcements = Announcement.objects.filter(is_active=True, publish_date__lte=timezone.now()).order_by('-publish_date')[:5]
        return Response({
            'upcoming_events': EventSerializer(events, many=True).data,
            'announcements': AnnouncementSerializer(announcements, many=True).data,
            'ads': []  # Şimdilik boş, ileride reklam modeli eklenebilir
        })

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-date', '-time')
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsNotBanned])
    def buy_ticket(self, request, pk=None):
        event = self.get_object()
        user = request.user
        if Ticket.objects.filter(event=event).count() >= event.capacity:
            return Response({'success': False, 'message': 'Etkinlik kontenjanı dolu.'}, status=400)
        if Ticket.objects.filter(event=event, user=user).exists():
            return Response({'success': False, 'message': 'Bu etkinlik için zaten bilet aldınız.'}, status=400)
        ticket = Ticket.objects.create(
            user=user,
            event=event,
            code=get_random_string(12)
        )
        return Response({'success': True, 'ticket': TicketSerializer(ticket).data})

class UserTicketsView(generics.ListAPIView):
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user).order_by('-purchased_at')
