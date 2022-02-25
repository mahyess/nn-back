from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Point


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_point(**kwargs):
    instance = kwargs.pop("instance")
    created = kwargs.pop("created")

    if created:
        Point.objects.create(user=instance)
