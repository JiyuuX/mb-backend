from django.urls import path
from . import views

urlpatterns = [
    path('ticker/', views.get_active_news, name='get_active_news'),
] 