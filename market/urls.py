from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryListView
from django.urls import path

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

# The router will automatically include the my_products action as /products/my_products/
urlpatterns = router.urls + [
    path('categories/', CategoryListView.as_view(), name='category-list'),
] 