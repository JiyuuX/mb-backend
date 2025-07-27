from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CategoryListView, DiscountVenueListView, AccommodationListView, AllProductsListView
from django.urls import path

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

# The router will automatically include the my_products action as /products/my_products/
urlpatterns = router.urls + [
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('all-products/', AllProductsListView.as_view(), name='all-products-list'),
    path('discount-venues/', DiscountVenueListView.as_view(), name='discount-venue-list'),
    path('accommodations/', AccommodationListView.as_view(), name='accommodation-list'),
] 