from rest_framework import serializers
from .models import Thread, Post, Comment
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_premium', 'profile_picture']

class ThreadSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    
    class Meta:
        model = Thread
        fields = ['id', 'title', 'creator', 'created_at', 'updated_at', 'is_pinned', 'is_locked']
        read_only_fields = ['creator', 'created_at', 'updated_at']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    thread = serializers.PrimaryKeyRelatedField(read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'thread', 'author', 'content', 'created_at', 'updated_at', 'is_edited', 'comment_count']
        read_only_fields = ['author', 'thread', 'created_at', 'updated_at']
    
    def get_comment_count(self, obj):
        return obj.comments.count()

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at', 'updated_at', 'is_edited']
        read_only_fields = ['author', 'post', 'created_at', 'updated_at'] 