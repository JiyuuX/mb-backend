from rest_framework import serializers
from .models import Thread, Post, Comment, Report
from users.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'is_premium', 'profile_picture', 'custom_username_color']

class ThreadSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Thread
        fields = ['id', 'title', 'creator', 'created_at', 'updated_at', 'is_pinned', 'is_locked', 'category', 'forum_type', 'university', 'likes_count', 'is_liked']
        read_only_fields = ['creator', 'created_at', 'updated_at', 'likes_count', 'is_liked']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user and user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False

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

class ReportSerializer(serializers.ModelSerializer):
    reporter = UserSerializer(read_only=True)
    thread = serializers.PrimaryKeyRelatedField(read_only=True)
    post = serializers.PrimaryKeyRelatedField(read_only=True)
    comment = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Report
        fields = ['id', 'thread', 'post', 'comment', 'reporter', 'category', 'reason', 'created_at']
        read_only_fields = ['id', 'reporter', 'created_at', 'thread', 'post', 'comment'] 