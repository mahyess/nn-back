from django.contrib.auth import get_user_model
from django.db.models import Q

# from namastenepal.posts.serializers import (
#     UserDetailSerializer
# )
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from namastenepal.accounts.serializers import GenderSerializer
from namastenepal.community.serializers import (
    # UserDetailSerializer,
    UserProfileSerializer,
)
from namastenepal.core.models import User
from namastenepal.points.serializers import PointSerializer
from .models import AuditLogs, Friend, Profile


class UserMiniSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    points = PointSerializer()

    class Meta:
        model = User
        fields = [
            "uid",
            "id",
            "username",
            "full_name",
            "points",
            "profile",
            "category",
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    points = PointSerializer()
    gender = GenderSerializer()
    is_friend = serializers.SerializerMethodField("_is_friend")

    def _is_friend(self, obj):
        user = self.context.get("user", None)
        if user:
            return Friend.objects.filter(
                Q(from_user=get_user_model().objects.get(id=obj.id), to_user=user.id)
                | Q(from_user=user.id, to_user=obj.id)
            ).exists()
        return None

    class Meta:
        model = User
        fields = [
            "uid",
            "id",
            "username",
            "gender",
            "email",
            "first_name",
            "last_name",
            "profile",
            "points",
            "online",
            "is_friend",
            "category",
        ]


class AuditLogSerializer(serializers.ModelSerializer):
    user = UserDetailSerializer()

    class Meta:
        model = AuditLogs
        fields = "__all__"


class UserProfileMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar", "bio", "coverpic"]


class UserSerializer(serializers.ModelSerializer):
    gender = GenderSerializer()
    points = PointSerializer()
    profile = UserProfileMiniSerializer()

    # last_seen = serializers.SerializerMethodField()
    # online = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "uid",
            "username",
            "first_name",
            "last_name",
            "online",
            "last_seen",
            "gender",
            "profile",
            "date_joined",
            "points",
            "category",
        )

    # def get_last_seen(self, obj):
    #     last_seen = cache.get('seen_%s' % obj.username)
    #     obj.last_seen = last_seen
    #     return last_seen

    # def get_online(self, obj):
    #     if obj.last_seen:
    #         now = datetime.datetime.now()
    #         delta = datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT)
    #         if now > obj.last_seen + delta:
    #             return False
    #         else:
    #             return True
    #     else:
    #         return False


class UserCardSerializer(serializers.ModelSerializer):
    profile = UserProfileMiniSerializer()
    profile_color = serializers.SerializerMethodField()

    @staticmethod
    def get_profile_color(obj):
        return obj.points.color_code

    class Meta:
        model = User
        fields = (
            "id",
            "uid",
            "username",
            "full_name",
            "profile",
            "profile_color",
        )


class FriendsSerializer(serializers.ModelSerializer):
    to_user = UserSerializer()

    class Meta:
        model = Friend
        fields = ("id", "to_user", "created_at")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        to_user_representation = representation.pop("to_user")
        for key in to_user_representation:
            representation[key] = to_user_representation[key]

        return representation


class ReceivedFriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer()

    class Meta:
        model = Friend
        fields = ("id", "from_user", "created_at")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        from_user_representation = representation.pop("from_user")
        for key in from_user_representation:
            representation[key] = from_user_representation[key]

        return representation


class SentFriendRequestSerializer(serializers.ModelSerializer):
    to_user = UserSerializer()

    class Meta:
        model = Friend
        fields = ("id", "to_user", "created_at")

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        to_user_representation = representation.pop("to_user")
        for key in to_user_representation:
            representation[key] = to_user_representation[key]

        return representation


class ViewProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["avatar", "coverpic", "birthdate", "city"]


class AvatarImageSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = Profile
        fields = ["avatar"]


class CoverImageSerializer(serializers.ModelSerializer):
    # FileField( max_length=None, use_url=True, required=False)
    coverpic = Base64ImageField()

    class Meta:
        model = Profile
        fields = ["coverpic"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["country", "city", "bio"]


class EditProfileSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "profile"]
