import re

from rest_framework import serializers
from rest_framework.fields import FileField, CharField

from namastenepal.community.serializers import CommunityForPostSerializer
from namastenepal.core.models import User, HashTag
from namastenepal.points.serializers import PointSerializer
from namastenepal.usermodule.serializers import (
    UserDetailSerializer,
    AvatarImageSerializer,
)
from .models import Post, Comment, Attachment


class PostIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["pid"]


class PostSlugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ["slug"]


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["comment"]


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ["url"]


class CreateAttachmentSerializer(serializers.ModelSerializer):
    # url = ImageField(use_url=True, required=False)

    class Meta:
        model = Attachment
        fields = "__all__"


class PostUserSerializer(serializers.ModelSerializer):
    profile = AvatarImageSerializer()
    points = PointSerializer()

    class Meta:
        model = User
        fields = ["uid", "full_name", "username", "profile", "points"]


class TagUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class PostSearchSerializer(serializers.ModelSerializer):
    # user = UserMiniSerializer()
    user = PostUserSerializer()
    community = CommunityForPostSerializer()
    attachments = serializers.SerializerMethodField()

    @staticmethod
    def get_attachments(obj):
        return [
            each.public_url
            for each in obj.attachments.filter(category=Attachment.IMAGE)
        ]

    def get_fields(self):
        fields = super(PostSearchSerializer, self).get_fields()
        fields["shared_post"] = PostSearchSerializer()
        return fields

    class Meta:
        model = Post
        fields = [
            "pid",
            "community",
            "user",
            "title",
            "slug",
            "body",
            "attachments",
            "total_likes",
            "total_comments",
            "timestamp",
        ]


class PostSerializer(serializers.ModelSerializer):
    # user = UserMiniSerializer()
    user = PostUserSerializer()
    tags = TagUserSerializer(many=True)
    community = CommunityForPostSerializer()
    attachments = serializers.SerializerMethodField()

    # body = serializers.SerializerMethodField()

    @staticmethod
    def get_attachments(obj):
        return [each.public_url for each in obj.attachments.all()]

    def get_fields(self):
        fields = super(PostSerializer, self).get_fields()
        fields["shared_post"] = PostSerializer()
        return fields

    class Meta:
        model = Post
        fields = [
            "pid",
            "community",
            "user",
            "title",
            "slug",
            "body",
            "shared_post",
            "attachments",
            "likes",
            "tags",
            "total_likes",
            "total_comments",
            "pinned",
            "reports",
            "timestamp",
        ]
        extra_kwargs = {"body": {"trim_whitespace": False}}


class CreatePostSerializer(serializers.ModelSerializer):
    pid = CharField(required=False)

    @staticmethod
    def hash_tags_validation(body):
        hash_tags = re.findall(r"(?:#([^\s]+))+", body)
        for hash_tag in hash_tags:
            if len(hash_tag) > 20:
                raise serializers.ValidationError(
                    "Hash tags cannot be more than 20 characters."
                )
        return hash_tags

    @staticmethod
    def hash_tags_linking(hash_tags):
        hash_tag_ins_list = []
        for hash_tag in hash_tags:
            ins, _ = HashTag.objects.get_or_create(title=hash_tag)
            hash_tag_ins_list.append(ins)
        return hash_tag_ins_list

    def update(self, validated_data, **kwargs):
        text = validated_data.get("title", "") + validated_data.get("body", "")
        hash_tags = self.hash_tags_validation(text)
        instance = Post.objects.update(**validated_data)
        instance.hash_tags.set(self.hash_tags_linking(hash_tags))
        return instance

    def create(self, validated_data):
        text = validated_data.get("title", "") + validated_data.get("body", "")
        hash_tags = self.hash_tags_validation(text)
        instance = Post.objects.create(**validated_data)
        instance.hash_tags.set(self.hash_tags_linking(hash_tags))
        return instance

    class Meta:
        model = Post
        fields = [
            "pid",
            "user",
            "community",
            "title",
            "body",
            "shared_post",
        ]


class CommentSerializer(serializers.ModelSerializer):
    user = PostUserSerializer()
    post = PostIdSerializer()
    user_vote_status = serializers.SerializerMethodField()

    def get_user_vote_status(self, obj):
        if self.context["request"].user.is_authenticated:
            user = self.context["request"].user
            if user in obj.up_votes.all():
                return 1
            elif user in obj.down_votes.all():
                return -1
            return 0
        return 0

    def get_fields(self):
        fields = super(CommentSerializer, self).get_fields()
        fields["replies"] = CommentSerializer(many=True)
        return fields

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "comment",
            "replies",
            "timestamp",
            "user",
            "total_votes",
            "user_vote_status",
        ]


# for Android
class CommentThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
