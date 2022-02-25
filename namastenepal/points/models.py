import os

from django.conf import settings
from django.db import models

from namastenepal.core.models import User


class Point(models.Model):
    user: User = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="points",
        null=True,
    )
    n_points = models.FloatField(default=0.00)
    p_points = models.FloatField(default=0.00)
    v_points = models.FloatField(default=0.00)
    color_code = models.CharField(max_length=10, null=True, blank=True)
    total_points = models.FloatField(default=0.00)

    def __str__(self):
        return f"{self.user.username} - {str(self.total_points)}"

    def save(self, *args, **kwargs):
        self.total_points = self.n_points + self.p_points + self.v_points
        if self.total_points < 0:
            self.color_code = "black"
        elif 0 < self.total_points <= 1000:
            self.color_code = "#2cc22c"
        elif 1000 < self.total_points <= 10000:
            self.color_code = "#3394e7"
        elif 10000 < self.total_points <= 100000:
            self.color_code = "red"
        elif 100000 < self.total_points <= 1000000:
            self.color_code = "purple"
        elif self.total_points > 1000000:
            self.color_code = "gold"
        else:
            self.color_code = "white"
        super(Point, self).save(*args, **kwargs)


def get_badge_file_path(instance, filename):
    return os.path.join(f"badges/{instance.token}", filename)


class Badge(models.Model):
    name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    width_field = models.IntegerField(default=0)
    height_field = models.IntegerField(default=0)
    icon = models.ImageField(
        upload_to=get_badge_file_path,
        blank=True,
        null=True,
        width_field="width_field",
        height_field="height_field",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
