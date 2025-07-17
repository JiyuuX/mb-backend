from rest_framework import serializers
from .models import Event, Ticket, Announcement

class EventSerializer(serializers.ModelSerializer):
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    time_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = '__all__'
    
    def get_time_formatted(self, obj):
        return obj.time.strftime('%H:%M')

class TicketSerializer(serializers.ModelSerializer):
    event = EventSerializer(read_only=True)
    
    class Meta:
        model = Ticket
        fields = '__all__'

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__' 