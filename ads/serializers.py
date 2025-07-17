from rest_framework import serializers
from .models import Advertisement

class AdvertisementSerializer(serializers.ModelSerializer):
    gif_url = serializers.SerializerMethodField()
    image_file = serializers.SerializerMethodField()
    video_file = serializers.SerializerMethodField()
    
    class Meta:
        model = Advertisement
        fields = ['id', 'title', 'description', 'company_name', 'gif_url', 'image_file', 'video_file', 'link_url', 'priority']
    
    def get_gif_url(self, obj):
        if obj.gif_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.gif_file.url)
            return obj.gif_file.url
        return None

    def get_image_file(self, obj):
        if obj.image_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image_file.url)
            return obj.image_file.url
        return None

    def get_video_file(self, obj):
        if obj.video_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None 