from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

class SubCategory(models.Model):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)
    name = models.CharField(max_length=64)

    class Meta:
        unique_together = ('category', 'name')

    def __str__(self):
        return f'{self.category.name} > {self.name}'

class Product(models.Model):
    STATUS_CHOICES = [
        ('new', 'Yeni'),
        ('used', '2. El'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.PROTECT, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='used')
    city = models.CharField(max_length=100, verbose_name="Şehir", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Favori sistemi
    favorited_by = models.ManyToManyField(get_user_model(), related_name='favorited_products', blank=True)

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return f"{self.product.title} - Image {self.id}"

class DiscountVenue(models.Model):
    name = models.CharField(max_length=100, verbose_name="İşletme Adı")
    image = models.ImageField(upload_to='discount_venues/', verbose_name="Tanıtım Resmi/GIF", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "İndirimli Mekan"
        verbose_name_plural = "İndirimli Mekanlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Accommodation(models.Model):
    name = models.CharField(max_length=100, verbose_name="Konaklama Adı")
    city = models.CharField(max_length=100, verbose_name="Şehir")
    description = models.TextField(verbose_name="Açıklama", blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fiyat")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")

    class Meta:
        verbose_name = "Konaklama"
        verbose_name_plural = "Konaklamalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.city}"
