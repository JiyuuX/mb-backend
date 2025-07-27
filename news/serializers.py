from rest_framework import serializers
from .models import News, CampusNews, DailySuggestion

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'content', 'is_active', 'priority', 'created_at']

class CampusNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampusNews
        fields = ['id', 'university', 'title', 'content', 'is_active', 'created_at']

class DailySuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySuggestion
        fields = ['id', 'text', 'is_active', 'created_at'] 