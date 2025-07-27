from django.urls import path
from . import views

urlpatterns = [
    path('ticker/', views.get_active_news, name='get_active_news'),
    path('campus/', views.get_campus_news, name='get_campus_news'),
    path('daily-suggestion/', views.get_daily_suggestion, name='get_daily_suggestion'),
] 