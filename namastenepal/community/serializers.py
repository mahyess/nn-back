from rest_framework import serializers
from namastenepal.community.models import Community, CommunityRequest
from namastenepal.core.models import User
from namastenepal.usermodule.models import Profile
from rest_framework.fields import FileField, CharField, ImageField
from namastenepal.accounts.serializers import GenderSerializer, PointSerializer, UserSerializer
# from namastenepal.posts.serializers import PostNotificationSerializer
from drf_extra_fields.fields import Base64ImageField


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = [
            'avatar',
            'coverpic',
            'avatar',
            'birthdate',
            'city',
            'bio'
        ]


class AdminProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = [
            'avatar',

        ]


class ImageField(serializers.ImageField):

    def to_internal_value(self, data):
                # if data is None image field was not uploaded
        if data:
            file_object = super(ImageField, self).to_internal_value(data)
            django_field = self._DjangoImageField()
            django_field.error_messages = self.error_messages
            django_field.to_python(file_object)
            return file_object
        return data


class UpdateCommunitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Community
        fields = ['name', 'description']


class CommunityAdminSerializer(serializers.ModelSerializer):
    profile = AdminProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'uid', 'profile']


class CommunitySerializer(serializers.ModelSerializer):
    subscribers = CommunityAdminSerializer(many=True)
    admin = CommunityAdminSerializer(many=True)

    class Meta:
        model = Community
        fields = [
            'id',
            'name',
            'slug',
            'background',
            'icon',
            'description',
            'subscribers',
            'admin',
            'subscriber_gender',
            'timestamp',
            'is_private',
        ]


class CommunitySearchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Community
        fields = [
            'id',
            'name',
            'slug',
            'background',
            'icon',
            'description',
            'total_subs',
        ]


class CommunityForPostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Community
        fields = [
            'id',
            'name',
            'slug',
            'icon',
        ]


class IconSerializer(serializers.ModelSerializer):
    icon = Base64ImageField()

    class Meta:
        model = Community
        fields = ['icon']


class BackgroundImageSerializer(serializers.ModelSerializer):
    # FileField( max_length=None, use_url=True, required=False)
    background = Base64ImageField()

    class Meta:
        model = Community
        fields = ['background']


class CommunityRequestSerializer(serializers.ModelSerializer):
    icon = Base64ImageField(required=False)
    background = Base64ImageField(required=False)
    # requester = UserSerializer()

    class Meta:
        model = CommunityRequest
        # optional_fields = ['icon', ]
        fields = ['requester', 'name', 'description', 'icon', 'background']

    def get_validation_exclusions(self):
        exclusions = super(CommunityRequestSerializer,
                           self).get_validation_exclusions()
        return exclusions + ['icon']
