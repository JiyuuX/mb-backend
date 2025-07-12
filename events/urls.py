from django.urls import path
from .views import UpcomingEventsListView, ActiveAnnouncementsListView, DashboardFeedView
 
urlpatterns = [
    path('upcoming-events/', UpcomingEventsListView.as_view(), name='upcoming-events'),
    path('announcements/', ActiveAnnouncementsListView.as_view(), name='announcements'),
    path('dashboard/', DashboardFeedView.as_view(), name='dashboard-feed'),
] 