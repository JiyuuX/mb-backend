from django.urls import path
from . import views

urlpatterns = [
    path('active/', views.get_active_ads, name='get_active_ads'),
    path('click/<int:ad_id>/', views.ad_click, name='ad_click'),
] 