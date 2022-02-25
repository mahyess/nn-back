import os
import re
import time
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import ValidationError

from namastenepal.community.models import Community
from namastenepal.core.models import HashTag, User
from namastenepal.points.pointSystem import multiplier
from namastenepal.usermodule.models import AuditLogs, Tag
from .abstract_models import SoftDeletableManager


def get_collection_path(_, filename):
    return os.path.join("samaj/image-collections/", filename)


class Attachment(models.Model):
    # width_field = models.IntegerField(default=0)
    # height_field = models.IntegerField(default=0)
    url = models.FileField(
        upload_to=get_collection_path,
        # width_field="width_field",
        # height_field="height_field",
        null=True,
        blank=True,
    )
    IMAGE = "i"
    VIDEO = "v"
    DOCUMENT = "d"
    CATEGORY_CHOICES = ((IMAGE, "Image"), (VIDEO, "Video"), (DOCUMENT, "Document"))
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default=IMAGE)

    def __str__(self):
        return str(self.url)

    @property
    def public_url(self):
        return settings.MEDIA_URL + str(self.url)


class Post(models.Model):
    # for deleted posts to be hidden from outside, but remain in database
    objects = SoftDeletableManager()
    archive_objects = models.Manager()
    # --------------------------------------------

    pid = models.CharField(max_length=100, unique=True, null=True, blank=True)
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name="community_posts",
        blank=True,
        null=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_posts"
    )
    title: str = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, max_length=50)
    shared_post = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="sharers", null=True, blank=True
    )
    body = models.TextField(blank=True, null=True)
    attachments = models.ManyToManyField(Attachment, blank=True, related_name="post")
    likes: User = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="liked_posts"
    )
    pinned = models.BooleanField(default=False)
    tags = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="tagged_posts"
    )
    reports: User = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="reported_posts"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(blank=True, null=True)
    hash_tags = models.ManyToManyField(
        HashTag, blank=True, related_name="hash_tag_posts"
    )

    def __str__(self):
        return self.body if self.body else self.title

    @property
    def post_priority(self):
        if self.community:
            return multiplier(self.community.priority)
        return 1

    @property
    def total_comments(self):
        return Comment.objects.filter(post_id=self.id).count()

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def total_reports(self):
        return self.reports.count()

    def clean(self):
        if not self.community:
            self.title = ""
        if self.community:
            if self.user not in self.community.subscribers.all():
                raise ValidationError(
                    detail={"user": "you are not authorized to post."},
                    code=status.HTTP_401_UNAUTHORIZED,
                )

            if not self.title or self.title == "" or self.title == "undefined":
                raise ValidationError(
                    detail={"Title is required."}, code=status.HTTP_400_BAD_REQUEST
                )

            if len(self.title) > 200:
                raise ValidationError(
                    detail={"Title length should not exceed 200."},
                    code=status.HTTP_400_BAD_REQUEST,
                )

        if self.body:
            if len(self.body) > 3500:
                raise ValidationError(
                    detail={"Body length should not exceed 3500."},
                    code=status.HTTP_400_BAD_REQUEST,
                )

    def save(self, *args, **kwargs):
        if not self.id:
            self.pid = uuid.uuid4().hex
            slug_name = (
                (self.title[:8] if self.title else self.body[:8])
                + "-"
                + time.strftime("%Y%m%d-%H%M%S")
            )
            self.slug = slugify(slug_name)

        self.full_clean()
        super(Post, self).save(*args, **kwargs)

    def delete(self, **kwargs):
        """Softly delete the entry"""
        self.deleted = timezone.now()
        self.save()

    def hard_delete(self):
        """Remove the entry from the database permanently"""
        super().delete()


class Comment(models.Model):
    user: User = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user_comments"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments", null=True
    )
    comment = models.TextField(null=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )
    up_votes: User = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="up_votes"
    )
    down_votes: User = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="down_votes"
    )
    mentions = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="mentioned_comments"
    )
    discuss_group: User = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="discuss_group"
    )
    approved = models.BooleanField(blank=True, null=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment

    def clean(self):
        # print(self.user.is_authenticated)
        if not self.user.is_authenticated:
            raise ValidationError("Login is required to comment on a post.")
        if not self.comment or self.comment.strip(" \t\n\r") == "":
            raise ValidationError("Comment is required")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

        if not self.parent:  # if not reply
            if not self.discuss_group.exists():
                self.discuss_group.set(
                    (
                        self.user,
                        self.post.user,
                    )
                )
                self.approved = True
        else:
            if self.user in self.discuss_group.all():
                self.approved = True

        # get mentions from @username in comment
        mentions = re.findall(r"@(\S+)", self.comment)
        self.mentions.set(get_user_model().objects.filter(username__in=mentions))

    @property
    def total_votes(self):
        return self.up_votes.count() - self.down_votes.count()
