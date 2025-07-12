from rest_framework import serializers
from .models import Advertisement

class AdvertisementSerializer(serializers.ModelSerializer):
    gif_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Advertisement
        fields = ['id', 'title', 'description', 'company_name', 'gif_url', 'link_url', 'priority']
    
    def get_gif_url(self, obj):
        if obj.gif_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.gif_file.url)
            return obj.gif_file.url
        return None 