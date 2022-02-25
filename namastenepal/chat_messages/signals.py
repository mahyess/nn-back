from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver

from .models import (
    Message,
    ChatUsersGroup,
    ChatUsersGroupProfile,
)


@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def delete_deleted_user_messages(**kwargs):
    """delete messages on user delete
    :param kwargs: instance-> deleted user
    :return: None
    """

    instance = kwargs.pop("instance")

    Message.objects.filter(author=instance).delete()


@receiver(m2m_changed, sender=ChatUsersGroup.participants.through)
def create_chat_group_profile(**kwargs):
    action = kwargs.pop("action")
    user_group = kwargs.pop("instance")
    pk_set = kwargs.pop("pk_set")

    if action == "post_add" and user_group.participants.count() > 2:
        ChatUsersGroupProfile.objects.get_or_create(
            user_group=user_group,
        )
        for pk in pk_set:
            Message.objects.create(
                content=f"[[ACTIVITY]]:{get_user_model().objects.get(pk=pk).username} joined",
                group=user_group,
            )

    if action == "post_remove":
        ChatUsersGroupProfile.objects.get_or_create(
            user_group=user_group,
        )
        for pk in pk_set:
            Message.objects.create(
                content=f"[[ACTIVITY]]:{get_user_model().objects.get(pk=pk).username} left",
                group=user_group,
            )


@receiver(post_save, sender=ChatUsersGroup)
def group_created_message(**kwargs):
    user_group = kwargs.pop("instance")
    created = kwargs.pop("created")

    if created:
        Message.objects.create(content="[[ACTIVITY]]:start chat", group=user_group)


@receiver(post_save, sender=Message)
def update_recent_activity_in_users_group(**kwargs):
    message = kwargs.pop("instance")
    created = kwargs.pop("created")

    if created:
        message.group.save()
