from django.contrib import admin
from .models import News, CampusNews
from django import forms

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'priority', 'created_at')
    list_filter = ('is_active', 'priority', 'created_at')
    search_fields = ('title', 'content')
    list_editable = ('is_active', 'priority')
    ordering = ('-priority', '-created_at')

@admin.register(CampusNews)
class CampusNewsAdmin(admin.ModelAdmin):
    list_display = ('university', 'title', 'is_active', 'created_at')
    list_filter = ('university', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'university')
    list_editable = ('is_active',)
    ordering = ('-created_at',)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'university':
            universities = [
                "Abant İzzet Baysal Üniversitesi",
                "Adana Alparslan Türkeş Bilim ve Teknoloji Üniversitesi",
                "Adıyaman Üniversitesi",
                "Afyon Kocatepe Üniversitesi",
                "Afyonkarahisar Sağlık Bilimleri Üniversitesi",
                "Ağrı İbrahim Çeçen Üniversitesi",
                "Aksaray Üniversitesi",
                "Alanya Alaaddin Keykubat Üniversitesi",
                "Amasya Üniversitesi",
                "Anadolu Üniversitesi",
                "Ankara Hacı Bayram Veli Üniversitesi",
                "Ankara Üniversitesi",
                "Ankara Yıldırım Beyazıt Üniversitesi",
                "Antalya Bilim Üniversitesi",
                "Ardahan Üniversitesi",
                "Artvin Çoruh Üniversitesi",
                "Atatürk Üniversitesi",
                "Balıkesir Üniversitesi",
                "Bandırma Onyedi Eylül Üniversitesi",
                "Bartın Üniversitesi",
                "Batman Üniversitesi",
                "Bayburt Üniversitesi",
                "Bilecik Şeyh Edebali Üniversitesi",
                "Bingöl Üniversitesi",
                "Bitlis Eren Üniversitesi",
                "Boğaziçi Üniversitesi",
                "Bolu Abant İzzet Baysal Üniversitesi",
                "Burdur Mehmet Akif Ersoy Üniversitesi",
                "Bursa Teknik Üniversitesi",
                "Bursa Uludağ Üniversitesi",
                "Çanakkale Onsekiz Mart Üniversitesi",
                "Çankırı Karatekin Üniversitesi",
                "Çukurova Üniversitesi",
                "Dicle Üniversitesi",
                "Düzce Üniversitesi",
                "Ege Üniversitesi",
                "Erciyes Üniversitesi",
                "Erzincan Binali Yıldırım Üniversitesi",
                "Erzurum Teknik Üniversitesi",
                "Eskişehir Osmangazi Üniversitesi",
                "Eskişehir Teknik Üniversitesi",
                "Fırat Üniversitesi",
                "Galatasaray Üniversitesi",
                "Gaziantep Üniversitesi",
                "Gaziosmanpaşa Üniversitesi",
                "Gebze Teknik Üniversitesi",
                "Giresun Üniversitesi",
                "Gümüşhane Üniversitesi",
                "Hacettepe Üniversitesi",
                "Hakkari Üniversitesi",
                "Harran Üniversitesi",
                "Hatay Mustafa Kemal Üniversitesi",
                "Hitit Üniversitesi",
                "Iğdır Üniversitesi",
                "Isparta Uygulamalı Bilimler Üniversitesi",
                "İnönü Üniversitesi",
                "İskenderun Teknik Üniversitesi",
                "İstanbul Medeniyet Üniversitesi",
                "İstanbul Teknik Üniversitesi",
                "İstanbul Üniversitesi",
                "İstanbul Üniversitesi-Cerrahpaşa",
                "İzmir Bakırçay Üniversitesi",
                "İzmir Demokrasi Üniversitesi",
                "İzmir Katip Çelebi Üniversitesi",
                "İzmir Yüksek Teknoloji Enstitüsü",
                "Kafkas Üniversitesi",
                "Kahramanmaraş Sütçü İmam Üniversitesi",
                "Karabük Üniversitesi",
                "Karadeniz Teknik Üniversitesi",
                "Karamanoğlu Mehmetbey Üniversitesi",
                "Kastamonu Üniversitesi",
                "Kayseri Üniversitesi",
                "Kırıkkale Üniversitesi",
                "Kırklareli Üniversitesi",
                "Kırşehir Ahi Evran Üniversitesi",
                "Kilis 7 Aralık Üniversitesi",
                "Kocaeli Üniversitesi",
                "Konya Teknik Üniversitesi",
                "KTO Karatay Üniversitesi",
                "Malatya Turgut Özal Üniversitesi",
                "Manisa Celal Bayar Üniversitesi",
                "Mardin Artuklu Üniversitesi",
                "Marmara Üniversitesi",
                "Mersin Üniversitesi",
                "Muğla Sıtkı Koçman Üniversitesi",
                "Munzur Üniversitesi",
                "Muş Alparslan Üniversitesi",
                "Nevşehir Hacı Bektaş Veli Üniversitesi",
                "Niğde Ömer Halisdemir Üniversitesi",
                "Ondokuz Mayıs Üniversitesi",
                "Ordu Üniversitesi",
                "Osmaniye Korkut Ata Üniversitesi",
                "Pamukkale Üniversitesi",
                "Recep Tayyip Erdoğan Üniversitesi",
                "Sakarya Üniversitesi",
                "Samsun Üniversitesi",
                "Siirt Üniversitesi",
                "Sinop Üniversitesi",
                "Sivas Cumhuriyet Üniversitesi",
                "Süleyman Demirel Üniversitesi",
                "Şırnak Üniversitesi",
                "Tekirdağ Namık Kemal Üniversitesi",
                "Tokat Gaziosmanpaşa Üniversitesi",
                "Trabzon Üniversitesi",
                "Trakya Üniversitesi",
                "Tunceli Munzur Üniversitesi",
                "Uşak Üniversitesi",
                "Van Yüzüncü Yıl Üniversitesi",
                "Yalova Üniversitesi",
                "Yıldız Teknik Üniversitesi",
                "Yozgat Bozok Üniversitesi",
                "Zonguldak Bülent Ecevit Üniversitesi"
            ]
            kwargs['widget'] = forms.Select(choices=[(u, u) for u in universities])
        return super().formfield_for_dbfield(db_field, **kwargs) 