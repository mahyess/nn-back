from django.contrib.auth import get_user_model
from rest_framework import serializers

from namastenepal.usermodule.serializers import (
    UserCardSerializer,
)
from .models import (
    ChatUsersGroup,
    Message,
    ChatUsersGroupProfile,
    # MessageUsersGroupProfile,
)


class MessageSerializer(serializers.ModelSerializer):
    attachment = serializers.FileField(write_only=True)

    class Meta:
        model = Message
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation["author"]:
            author = representation.pop("author")
            representation["author"] = UserCardSerializer(
                get_user_model().objects.get(pk=author)
            ).data

        return {**representation, "id": instance.id.hex, "group": instance.group.id.hex}


class MessageCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["content", "created_at"]


class MessageUsersGroupCardSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    def get_title(self, obj):
        if hasattr(obj, "group_profile"):
            return obj.group_profile.name
        return obj.participants.exclude(id=self.context["request"].user.id).first().full_name

    def get_icon(self, obj):
        if hasattr(obj, "group_profile"):
            return obj.group_profile.icon.url
        return obj.participants.exclude(id=self.context["request"].user.id).first().profile.avatar.url

    @staticmethod
    def get_last_message(obj):
        return MessageCardSerializer(Message.objects.filter(group=obj).first()).data

    @staticmethod
    def get_unread_count(obj):
        return Message.objects.filter(group=obj, seen=False).count()

    class Meta:
        model = ChatUsersGroup
        fields = ["id", "title", "icon", "last_message", "unread_count"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {**representation, "id": instance.id.hex}


class MessageUsersGroupProfileSerializer(serializers.ModelSerializer):
    admin = UserCardSerializer()

    class Meta:
        model = ChatUsersGroupProfile
        fields = ["name", "admin", "icon", "description"]


class MessageUsersGroupDetailsSerializer(serializers.ModelSerializer):
    participants = UserCardSerializer(many=True)
    chat_type = serializers.SerializerMethodField()
    basic_info = serializers.SerializerMethodField()

    @staticmethod
    def get_chat_type(obj):
        if hasattr(obj, "group_profile"):
            return "Group"
        return "Friend"

    def get_basic_info(self, obj):
        # if working with group chat, wont need context
        if hasattr(obj, "group_profile"):
            return MessageUsersGroupProfileSerializer(obj.group_profile).data

        # serializer requires request context to find user
        if "request" in self.context:
            return UserCardSerializer(
                obj.participants.exclude(id=self.context["request"].user.id).first()
            ).data
        return None

    class Meta:
        model = ChatUsersGroup
        fields = ["id", "chat_type", "basic_info", "participants"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["id"] = str(representation["id"])

        return representation
