"""
Models related to messages
"""
import os
import uuid
from pathlib import Path

from django.conf import settings
from django.db import models
from rest_framework import status
from rest_framework.exceptions import ValidationError

from namastenepal.common import compress_image

User = settings.AUTH_USER_MODEL


def get_message_attachment_path(instance, filename):
    """
    :param instance: Message instance
    :param filename: File name of attachment of message
    :return: path where attachment is stored
    """

    return os.path.join(f"message_attachments/{filename}").format(instance.author.uid)


def get_group_icon_path(instance, filename):
    """
    :param instance: Message instance
    :param filename: File name of attachment of message
    :return: path where attachment is stored
    """

    return os.path.join(f"group-chat-icons/{filename}").format(
        instance.name if instance.name else instance.gid
    )


def validate_message_content(content):
    """
    :param content: message content
    :return: nothing. if not valid, raises Validation Error
    """

    if content is None or content == "" or content.isspace():
        raise ValidationError(
            detail="Content is empty/invalid",
            code="invalid",
        )


class ChatUsersGroup(models.Model):
    """
    Message User Group model for private individuals room
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    participants = models.ManyToManyField(User, related_name="users_group_participants")
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    latest_activity = models.DateTimeField(auto_now=True)

    def __str__(self):
        return " - ".join(self.participants.values_list("username", flat=True))


class ChatUsersGroupProfile(models.Model):
    """
    Message User Group model for group room
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user_group = models.OneToOneField(
        ChatUsersGroup,
        on_delete=models.CASCADE,
        related_name="group_profile",
    )
    name = models.CharField(max_length=20, default="Unnamed Group")
    admin = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="message_users_group_admin",
    )
    icon_width = models.IntegerField(default=0)
    icon_height = models.IntegerField(default=0)
    description: str = models.TextField(null=True, blank=True)
    icon = models.ImageField(
        upload_to=get_group_icon_path,
        width_field="icon_width",
        height_field="icon_height",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.icon:
            self.icon = compress_image(
                Path("namastenepal/chat_messages/templates/static/icon.jpg")
            )
        super().save(*args, **kwargs)


class Message(models.Model):
    """
    Group Message model for group
    """

    id = models.UUIDField(
        primary_key=True, null=False, default=uuid.uuid4, editable=False
    )
    author: User = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.DO_NOTHING,
        related_name="authored_group_messages",
    )
    group = models.ForeignKey(
        ChatUsersGroup,
        related_name="messages",
        on_delete=models.DO_NOTHING,
        null=True,
    )
    attachment = models.FileField(
        upload_to=get_message_attachment_path,
        blank=True,
        null=True,
    )

    content = models.TextField(null=True)
    seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        if self.author:
            return self.author.username
        return self.content

    class Meta:
        ordering = ("-created_at",)

    def clean(self):
        is_activity = self.content[:13] == "[[ACTIVITY]]:"
        if not self.author and not is_activity:
            raise ValidationError(
                detail={"author": "Author is required"},
                code=status.HTTP_401_UNAUTHORIZED,
            )

        if (
            not is_activity
            and not self.group.participants.filter(pk=self.author.pk).exists()
        ):
            raise ValidationError(
                detail={"author": "author not in group"},
                code=status.HTTP_401_UNAUTHORIZED,
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
