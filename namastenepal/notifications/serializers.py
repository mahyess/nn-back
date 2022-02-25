"""
notification serializer
"""
from rest_framework import serializers

from .models import (
    Notification,
    PostNotification,
    CommentNotification,
    CommunityNotification,
    FriendNotification,
)
from namastenepal.accounts.serializers import UserMiniSerializer


class PostNotificationSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category_verbose")
    post_slug = serializers.CharField(source="post.slug")

    class Meta:
        model = PostNotification
        fields = ["category", "post_slug"]


class CommentNotificationSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category_verbose")
    post_id = serializers.SlugField(source="comment.post.id")
    comment_id = serializers.CharField(source="comment.id")

    class Meta:
        model = CommentNotification
        fields = ["comment_id", "post_id", "category"]


class CommunityNotificationSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category_verbose")
    community_id = serializers.CharField(source="community.id")

    class Meta:
        model = CommunityNotification
        fields = ["community_id", "category"]


class FriendNotificationSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category_verbose")
    friend_username = serializers.CharField(source="friend.username")

    class Meta:
        model = FriendNotification
        fields = ["friend_username", "category"]


class NotificationSerializer(serializers.ModelSerializer):
    details = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    @staticmethod
    def get_user(obj):
        return UserMiniSerializer(obj.sender).data

    @staticmethod
    def get_details(obj):
        if hasattr(obj, "post_notification"):
            return PostNotificationSerializer(obj.post_notification).data
        elif hasattr(obj, "comment_notification"):
            return CommentNotificationSerializer(obj.comment_notification).data
        elif hasattr(obj, "community_notification"):
            return CommunityNotificationSerializer(obj.community_notification).data
        elif hasattr(obj, "friend_notification"):
            return FriendNotificationSerializer(obj.friend_notification).data
        return None

    class Meta:
        model = Notification
        fields = [
            "id",
            "user",
            "details",
            "action",
            "seen",
            "timestamp",
        ]
