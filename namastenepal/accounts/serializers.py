from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from namastenepal.core.models import User, Gender
from namastenepal.points.serializers import BadgeSerializer, PointSerializer
from namastenepal.usermodule.models import Profile


class GenderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Gender
        fields = [
            'title'
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    badges = BadgeSerializer(many=True)

    class Meta:
        model = Profile
        fields = [
            'avatar',
            'coverpic',
            'birthdate',
            'badges',
            'city',
            'country',
            'bio'
        ]


class UserProfileMiniSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = [
            'avatar',
            'bio'
        ]


class UserMiniSerializer(serializers.ModelSerializer):
    profile = UserProfileMiniSerializer()
    points = PointSerializer()

    class Meta:
        model = User
        fields = [
            'id', 'uid', 'username', 'first_name', 'last_name', 'profile', 'date_joined', 'points'
        ]


class UserSerializer(serializers.ModelSerializer):
    gender = GenderSerializer()
    profile = UserProfileSerializer()
    points = PointSerializer()

    class Meta:
        model = User
        fields = ('id', 'uid', 'username', 'phone_number', 'first_name',
                  'last_name', 'gender', 'profile', 'points', 'online', 'last_seen')


class UserSerializerWithToken(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    @staticmethod
    def get_token(obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('token', 'username', 'password')


class CreateProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = [
            'avatar',
            'coverpic',
            'birthdate',
            'country'
        ]


class CreateUserSerializer(serializers.ModelSerializer):
    gender = GenderSerializer()

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'first_name',
            'last_name',
            'gender'
        ]


class TagProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ['avatar']


class TagUserSerializer(serializers.ModelSerializer):
    profile = TagProfileSerializer()

    class Meta:
        model = User
        fields = ['uid', 'username', 'profile']


class MentionUserSerializer(serializers.ModelSerializer):
    pass
