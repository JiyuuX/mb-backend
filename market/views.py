from django.shortcuts import render
from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import ProductImage
from rest_framework import permissions
from rest_framework.views import APIView
from .serializers import CategorySerializer
from .models import Category
from users.permissions import IsNotBanned
from .models import DiscountVenue
from .serializers import DiscountVenueSerializer
from .models import Accommodation
from .serializers import AccommodationSerializer
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination

# Create your views here.

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.seller == request.user

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerOrReadOnly, IsNotBanned]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        
        # Eğer yeni görseller yüklendiyse, eski görselleri sil
        if 'images' in request.FILES:
            # Eski görselleri sil
            instance.images.all().delete()
            
        self.perform_update(serializer)
        return Response(serializer.data)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post', 'put'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        product = self.get_object()
        
        # PUT request ise (güncelleme), eski görselleri sil
        if request.method == 'PUT':
            product.images.all().delete()
        
        # Yeni görselleri ekle
        images = request.FILES.getlist('images')
        if images:
            for image_file in images:
                ProductImage.objects.create(product=product, image=image_file)
            return Response({'success': True, 'message': 'Görseller güncellendi.'})
        
        # Tek görsel için eski yöntem (geriye uyumluluk)
        image_file = request.FILES.get('image')
        if image_file:
            ProductImage.objects.create(product=product, image=image_file)
            return Response({'success': True, 'message': 'Görsel yüklendi.'})
        
        return Response({'success': False, 'message': 'Görsel bulunamadı.'}, status=400)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsNotBanned])
    def my_products(self, request):
        products = Product.objects.filter(seller=request.user).order_by('-created_at')
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsNotBanned])
    def toggle_favorite(self, request, pk=None):
        product = self.get_object()
        user = request.user
        
        if product.favorited_by.filter(id=user.id).exists():
            product.favorited_by.remove(user)
            return Response({'success': True, 'message': 'Favorilerden çıkarıldı.', 'is_favorited': False})
        else:
            product.favorited_by.add(user)
            return Response({'success': True, 'message': 'Favorilere eklendi.', 'is_favorited': True})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated, IsNotBanned])
    def my_favorites(self, request):
        products = Product.objects.filter(favorited_by=request.user).order_by('-created_at')
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)

class CategoryListView(APIView):
    def get(self, request):
        categories = Category.objects.prefetch_related('subcategories').all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

class DiscountVenueListView(APIView):
    def get(self, request):
        venues = DiscountVenue.objects.filter(is_active=True).order_by('-created_at')
        serializer = DiscountVenueSerializer(venues, many=True)
        return Response({'success': True, 'venues': serializer.data})

class AccommodationListView(APIView):
    def get(self, request):
        city = request.GET.get('city')
        accommodations = Accommodation.objects.filter(is_active=True)
        if city:
            accommodations = accommodations.filter(city__iexact=city)
        serializer = AccommodationSerializer(accommodations, many=True)
        return Response({'success': True, 'accommodations': serializer.data})

class AllProductsListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def get(self, request):
        # Pagination
        page = int(request.GET.get('page', 1))
        page_size = 50
        start = (page - 1) * page_size
        end = start + page_size
        
        # Search functionality
        search_query = request.GET.get('search', '')
        
        # Base queryset - newest first
        products = Product.objects.all().order_by('-created_at')
        
        # Apply search filter if query provided
        if search_query:
            products = products.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(subcategory__name__icontains=search_query) |
                Q(city__icontains=search_query)
            )
        
        # Get total count for pagination info
        total_count = products.count()
        
        # Apply pagination
        products = products[start:end]
        
        # Serialize products
        serializer = ProductSerializer(products, many=True, context={'request': request})
        
        return Response({
            'success': True,
            'products': serializer.data,
            'pagination': {
                'current_page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size,
                'has_next': end < total_count,
                'has_previous': page > 1
            }
        })

class FreeProductsListView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsNotBanned]
    
    def get(self, request):
        # Fiyatı 0 TL olan ürünleri getir
        free_products = Product.objects.filter(price=0).order_by('-created_at')
        
        # Serialize products
        serializer = ProductSerializer(free_products, many=True, context={'request': request})
        
        return Response({
            'success': True,
            'products': serializer.data,
            'total_count': free_products.count()
        })

# Sabit kategori dict ve force coding kaldırıldı. Kategori endpointi serializer ile model tabanlı olacak.
