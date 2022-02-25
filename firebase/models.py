from django.conf import settings
from django.db import models

from namastenepal.community.models import Community
from namastenepal.core.models import User


# Create your models here.
class Token(models.Model):
    user: User = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="tokens", on_delete=models.CASCADE
    )
    token: str = models.CharField(max_length=255)

    ANDROID = "a"
    IOS = "i"
    WEB = "w"
    CATEGORY_CHOICES = ((ANDROID, "Android"), (IOS, "iOS"), (WEB, "Web"))
    category: str = models.CharField(
        max_length=1, choices=CATEGORY_CHOICES, default=ANDROID
    )

    def __str__(self):
        return f"{self.user.username} - {self.token}"


class Topic(models.Model):
    title: str = models.CharField(max_length=255)
    subscribers: Token = models.ManyToManyField(Token, related_name="topics")

    def __str__(self):
        return self.title
