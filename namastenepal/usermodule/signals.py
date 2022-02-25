from django.db.models import Q
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver

from namastenepal.chat_messages.models import ChatUsersGroup, Message
from namastenepal.core.models import User
from .models import (
    CelebVerification,
    AuditLogs,
    Friend,
    BlockedUser,
    FriendRequest,
    Profile,
)
from ..common import get_exact_match


@receiver(post_save, sender=User)
def create_user_profile(**kwargs):
    instance = kwargs.pop("instance")
    created = kwargs.pop("created")

    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(**kwargs):
    instance = kwargs.pop("instance")

    instance.profile.save()


@receiver(post_save, sender=Friend)
def add_versa_friend(**kwargs):
    instance = kwargs.pop("instance", None)
    created = kwargs.pop("created", None)

    if created:
        Friend.objects.get_or_create(
            from_user=instance.to_user, to_user=instance.from_user
        )


@receiver(post_delete, sender=Friend)
def clear_friend_traces(**kwargs):
    instance = kwargs.pop("instance", None)

    user1 = instance.from_user
    user2 = instance.to_user

    Friend.objects.filter(
        Q(from_user=user1, to_user=user2) | Q(from_user=user2, to_user=user1)
    ).delete()
    FriendRequest.objects.filter(
        Q(from_user=user1, to_user=user2) | Q(from_user=user2, to_user=user1)
    ).delete()
    # Message.objects.filter(
    #     Q(author=user1, message_to=user2) | Q(author=user2, message_to=user1)
    # ).delete()
    # RecentChat.objects.filter(
    #     Q(author=user2, message_to=user1) | Q(author=user1, message_to=user2)
    # ).delete()
    # ChatUsersGroup.objects.annotate(
    #     participants_ids=SubqueryAggregate("participants__id", Aggregate=ArrayAgg)
    # ).filter(
    #     participants_ids=Array(user1.id, user2.id)
    #     # Q(user1=user2, user2=user1) | Q(user1=user1, user2=user2)
    # ).delete()
    group = get_exact_match(ChatUsersGroup, "participants", [user1.id, user2.id])
    Message.objects.filter(group__in=group).delete()
    group.delete()


@receiver(post_save, sender=FriendRequest)
def accept_friend_request(**kwargs):
    instance = kwargs.pop("instance", None)
    created = kwargs.pop("created", None)

    if not created and instance.accepted:
        Friend.objects.filter(
            Q(from_user=instance.from_user, to_user=instance.to_user)
            | Q(from_user=instance.to_user, to_user=instance.from_user)
        ).get_or_create(
            defaults={"from_user": instance.from_user, "to_user": instance.to_user}
        )


@receiver(m2m_changed, sender=BlockedUser.blocked_users.through)
def unfriend_after_block(**kwargs):
    instance = kwargs.pop("instance", None)
    action = kwargs.pop("action", None)
    pk_set = kwargs.pop("pk_set", None)

    if action == "post_add":
        for f_id in pk_set:
            Friend.objects.filter(
                Q(from_user__pk=instance.user.pk, to_user__pk=f_id)
                | Q(from_user__pk=f_id, to_user__pk=instance.user.pk)
            ).delete()


@receiver(post_save, sender=CelebVerification)
def respond_user_verification_request(**kwargs):
    sender = kwargs.pop("sender", None)
    instance = kwargs.pop("instance", None)
    created = kwargs.pop("created", None)

    task = AuditLogs.objects.create(user=instance.user)

    if created:
        task.action = f"requested to be verified as {instance.category_verbose}"
    else:
        if instance.status_verbose == "Accepted":
            sender.category = instance.category
        task.action = f"requested to be verified as {instance.category_verbose}, which was {instance.status_verbose}"
        CelebVerification.objects.filter(user=instance.user).delete()

    task.save()
