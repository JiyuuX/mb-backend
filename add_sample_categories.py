import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from market.models import Category, SubCategory

CATEGORIES = {
    "Kadın Giyim": ["Elbise", "T-Shirt", "Pantolon", "Etek", "Ceket", "Bluz", "Çanta&Cüzdan", "Ayakkabı", "Takı & Aksesuar"],
    "Erkek Giyim": ["T-Shirt", "Gömlek", "Pantolon", "Ceket", "Ayakkabı", "Çanta&Cüzdan", "Aksesuar"],
    "Çocuk Giyim": ["Kız Çocuk", "Erkek Çocuk", "Bebek", "Ayakkabı", "Aksesuar", "Çanta&Cüzdan"],
    "Ayakkabı": ["Kadın Ayakkabı", "Erkek Ayakkabı", "Çocuk Ayakkabı", "Spor Ayakkabı", "Sandalet", "Çanta&Cüzdan"],
    "Çanta & Aksesuar": ["Kadın Çanta&Cüzdan", "Erkek Çanta&Cüzdan", "Sırt Çantası", "Cüzdan", "Şapka", "Gözlük"],
    "Saat & Takı": ["Kol Saati", "Bileklik", "Küpe", "Kolye", "Yüzük"],
    "Spor & Outdoor": ["Spor Giyim", "Spor Ayakkabı", "Outdoor Ekipman", "Kamp Malzemeleri", "Çanta&Cüzdan"],
    "Elektronik": ["Telefon", "Bilgisayar", "Tablet", "Aksesuar", "Kulaklık", "Çanta&Cüzdan"],
    "Ev & Yaşam": ["Dekorasyon", "Mutfak", "Mobilya", "Aydınlatma", "Ev Tekstili", "Çanta&Cüzdan"],
    "Kitap & Dergi": ["Roman", "Çocuk Kitapları", "Eğitim", "Dergi", "Çanta&Cüzdan"],
    "Oyuncak": ["Eğitici Oyuncak", "Peluş", "Puzzle", "Araba", "Çanta&Cüzdan"],
    "Anne & Bebek": ["Bebek Giyim", "Bebek Arabası", "Emzirme", "Oyuncak", "Çanta&Cüzdan"],
    "Kozmetik & Kişisel Bakım": ["Makyaj", "Cilt Bakımı", "Saç Bakımı", "Parfüm", "Çanta&Cüzdan"],
    "Diğer": ["Diğer"],
}

# Eğer Saat ana kategorisi yoksa, Kadın ve Erkek Giyim'e 'Saat' alt kategorisi ekle
if "Saat & Takı" not in CATEGORIES:
    for main_cat in ["Kadın Giyim", "Erkek Giyim"]:
        if "Saat" not in CATEGORIES[main_cat]:
            CATEGORIES[main_cat].append("Saat")

# Her ana kategoriye 'Diğer' alt kategorisi ekle
for cat_name in CATEGORIES:
    if "Diğer" not in CATEGORIES[cat_name]:
        CATEGORIES[cat_name].append("Diğer")

for cat_name, subcats in CATEGORIES.items():
    cat, _ = Category.objects.get_or_create(name=cat_name)
    for subcat_name in subcats:
        SubCategory.objects.get_or_create(category=cat, name=subcat_name)

print('Örnek kategoriler ve alt kategoriler eklendi.') 