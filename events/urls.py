from django.urls import path, include
from .views import UpcomingEventsListView, ActiveAnnouncementsListView, DashboardFeedView, UserTicketsView
from rest_framework.routers import DefaultRouter
from .views import EventViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')

urlpatterns = [
    path('', include(router.urls)),
    path('upcoming-events/', UpcomingEventsListView.as_view(), name='upcoming-events'),
    path('announcements/', ActiveAnnouncementsListView.as_view(), name='announcements'),
    path('dashboard/', DashboardFeedView.as_view(), name='dashboard-feed'),
    path('my-tickets/', UserTicketsView.as_view(), name='user-tickets'),
] 