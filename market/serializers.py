from rest_framework import serializers
from .models import Product, ProductImage, Category, SubCategory
from users.serializers import UserProfileSerializer

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories']

class ProductSerializer(serializers.ModelSerializer):
    seller = UserProfileSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    subcategory = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all())
    category_detail = CategorySerializer(source='category', read_only=True)
    subcategory_detail = SubCategorySerializer(source='subcategory', read_only=True)
    is_favorited = serializers.SerializerMethodField()
    favorite_count = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__' 

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(id=request.user.id).exists()
        return False

    def get_favorite_count(self, obj):
        return obj.favorited_by.count() 