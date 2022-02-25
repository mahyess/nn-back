from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CommunityRequest, Community


@receiver(post_save, sender=CommunityRequest)
def create_samaj_on_request_accept(**kwargs):
    """create samaj on community request accept with requested details"""
    instance = kwargs.pop("instance")
    created = kwargs.pop("created")

    if not created and instance.status == CommunityRequest.ACCEPTED:
        created_community = Community.objects.create(
            name=instance.name,
            description=instance.description,
        )
        created_community.admin.add(instance.requester)
        created_community.save()
