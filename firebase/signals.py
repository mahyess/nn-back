from django.db.models.signals import post_save
from django.dispatch import receiver

from namastenepal.notifications.models import Notification
from namastenepal.notifications.serializers import NotificationSerializer
from .models import Topic
from namastenepal.community.models import Community
from .sdk import send_multicast


@receiver(post_save, sender=Community)
def create_topic_for_samaj(**kwargs):
    created = kwargs.pop("created")
    instance = kwargs.pop("instance")

    if created:
        Topic.objects.create(title=instance.name)


@receiver(post_save, sender=Notification)
def send_fcm_notification_on_create(**kwargs):
    notification = kwargs.pop("instance")
    created = kwargs.pop("created")
    if created:
        user_fcm_tokens = list(
            notification.user.tokens.all().values_list("token", flat=True)
        )

        if len(user_fcm_tokens):
            send_multicast(
                tokens=user_fcm_tokens, data=NotificationSerializer(notification).data
            )
