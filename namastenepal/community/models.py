"""
Models related to Community App
"""
import os
import uuid
from pathlib import Path

from django.db import models
from django.template.defaultfilters import slugify
from rest_framework import status
from rest_framework.exceptions import ValidationError

from namastenepal.core.models import User, Gender
from ..common import compress_image


def get_path(instance, filename):
    return os.path.join(f"samaj/{instance.name}/", filename).format()


class Community(models.Model):
    """
    samaj
    """

    id: str = models.CharField(
        max_length=255, unique=True, primary_key=True, editable=False
    )
    name: str = models.CharField(max_length=255, unique=True)
    slug: str = models.SlugField(null=True, blank=True, max_length=1000)
    background = models.ImageField(
        upload_to=get_path,
        width_field="width_field",
        height_field="height_field",
        null=True,
        blank=True,
    )
    width_field = models.IntegerField(default=0)
    height_field = models.IntegerField(default=0)
    description: str = models.TextField()
    icon = models.ImageField(
        upload_to=get_path,
        width_field="width_field",
        height_field="height_field",
        null=True,
        blank=True,
    )
    subscribers = models.ManyToManyField(User, related_name="subscribe", blank=True)
    admin = models.ManyToManyField(User, related_name="admin", blank=True)
    subscriber_gender: Gender = models.ForeignKey(
        Gender, null=True, blank=True, on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_private = models.BooleanField(default=False)

    # priority for points multiplier
    CRITICAL = "cr"
    VERY_HIGH = "vh"
    HIGH = "hi"
    MEDIUM = "md"
    LOW = "lo"
    PRIORITY_CHOICES = [
        (CRITICAL, "Critical"),
        (VERY_HIGH, "Very_high"),
        (HIGH, "High"),
        (MEDIUM, "Medium"),
        (LOW, "Low"),
    ]
    priority = models.CharField(
        max_length=2,
        choices=PRIORITY_CHOICES,
        default=MEDIUM,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "samaj"

    # @property
    # def get_priority_choices(self):
    #     return self.PRIORITY_CHOICES

    @property
    def total_subs(self):
        return self.subscribers.count()

    @property
    def subscribers_list(self):
        return [subscriber.id for subscriber in self.subscribers.all()]

    @property
    def admin_list(self):
        return [admin.id for admin in self.admin.all()]

    def save(self, *args, **kwargs):
        pre_ins = None
        if not self.id:
            self.id = str(uuid.uuid4().hex)
            self.slug = slugify(self.name)
        else:
            pre_ins = Community.objects.get(id=self.id)

        if not self.icon:
            self.icon = compress_image(
                Path("namastenepal/community/templates/static/icon.jpg")
            )
        elif pre_ins:
            if not self.icon == pre_ins.icon:
                self.icon = compress_image(self.icon)
        else:
            self.icon = compress_image(self.icon)

        if not self.background:
            self.background = compress_image(
                Path("namastenepal/community/templates/static/background.jpg")
            )
        elif pre_ins:
            if not self.background == pre_ins.background:
                self.background = compress_image(self.background)
        else:
            self.background = compress_image(self.background)

        super(Community, self).save(*args, **kwargs)


class CommunityRequest(models.Model):
    """community request from users"""

    requester = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000, unique=True)
    description = models.TextField()
    width_field = models.IntegerField(default=0)
    height_field = models.IntegerField(default=0)
    background = models.ImageField(
        upload_to=get_path,
        width_field="width_field",
        height_field="height_field",
        null=True,
        blank=True,
    )
    icon = models.ImageField(
        upload_to=get_path,
        width_field="width_field",
        height_field="height_field",
        null=True,
        blank=True,
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    REQUESTED = "rq"
    DECLINED = "dc"
    ACCEPTED = "ac"
    STATUS_CHOICES = [
        (REQUESTED, "Requested"),
        (DECLINED, "Declined"),
        (ACCEPTED, "Accepted"),
    ]
    status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default=REQUESTED,
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.clean()
        if Community.objects.filter(name=self.name).exists():
            raise ValidationError(
                detail={"name": "Community with this name already exists."},
                code=status.HTTP_400_BAD_REQUEST,
            )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "samaj request"
