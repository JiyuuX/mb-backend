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

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        product = self.get_object()
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

# Sabit kategori dict ve force coding kaldırıldı. Kategori endpointi serializer ile model tabanlı olacak.
