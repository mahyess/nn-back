import hashlib
import os
from datetime import datetime

from django.db import models
from django.db.models import Q
from django_countries.fields import CountryField
from rest_framework.exceptions import ValidationError

# from namastenepal.chat_messages.models import (
#     User,
#     RecentMessage,
#     Message,
#     MessageUsersGroup,
# )
from namastenepal.core.models import User
from namastenepal.points.models import Badge, Point


class Tag(models.Model):
    title = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)


def get_profile_image_file_path(instance, filename):
    return os.path.join(f"profileImages/{instance.user_id}", filename)


def get_cover_image_file_path(instance, filename):
    return os.path.join(f"coverImages/{instance.user_id}", filename)


def get_path(gender):
    return os.path.join("img/", f"{gender}.png")


def get_badge_file_path(instance, filename):
    return os.path.join(f"badges/{instance.token}", filename)


class Profile(models.Model):
    user: User = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )

    badges: Badge = models.ManyToManyField(
        Badge, blank=True, related_name="badge_getters"
    )
    # interests = models.ManyToManyField()
    is_verified = models.BooleanField(default=False)
    width_field = models.IntegerField(default=0)
    height_field = models.IntegerField(default=0)
    avatar = models.ImageField(
        upload_to=get_profile_image_file_path,
        blank=True,
        null=True,
        width_field="width_field",
        height_field="height_field",
    )
    coverpic = models.ImageField(
        upload_to=get_cover_image_file_path,
        blank=True,
        null=True,
        width_field="width_field",
        height_field="height_field",
    )
    birthdate = models.DateField(blank=True, null=True)
    country = CountryField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    hometown = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if not self.avatar:
            if self.user.gender:
                self.avatar = get_path(str(self.user.gender))
            else:
                self.avatar = get_path("placeholder")

        super(Profile, self).save(*args, **kwargs)


class UserVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    v_code = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        token1 = self.user.username
        token2 = hashlib.sha1(os.urandom(1)).hexdigest()

        self.v_code = f"{str(token1)}-{str(token2)}"

        super(UserVerification, self).save(*args, **kwargs)


class TermsConditions(models.Model):
    content = models.TextField(blank=True, null=True)


class AuditLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logs")

    action = models.CharField(max_length=255)
    slug = models.CharField(max_length=1000, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class Friend(models.Model):
    from_user = models.ForeignKey(
        User, models.CASCADE, related_name="from_user", null=True
    )
    to_user = models.ForeignKey(User, models.CASCADE, related_name="to_user", null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User #{self.from_user_id} is friends with #{self.to_user_id}"

    # @property
    # def recent_message(self):
    #     message = RecentMessage.objects.filter(
    #         Q(author=self.from_user, message_to=self.to_user)
    #         | Q(author=self.to_user, message_to=self.from_user)
    #     )
    #     if message:
    #         for msg in message:
    #             return {
    #                 "id": str(msg.id),
    #                 "from": msg.author.username,
    #                 "to": msg.message_to.username,
    #                 "content": msg.content[:30],
    #                 "seen": msg.seen,
    #                 "created_at": str(msg.created_at),
    #             }
    #         return None

    @staticmethod
    def check_friend(from_user, to_user):
        return Friend.objects.filter(
            Q(from_user=from_user, to_user=to_user)
            & Q(from_user=to_user, to_user=from_user)
        ).exists()

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.from_user == self.to_user:
            raise ValidationError("Users cannot be friends with themselves.")

        # if self.check_friend(self.from_user, self.to_user) == False:
        #     raise ValidationError("already exists.")

        super(Friend, self).save(*args, **kwargs)


class FriendRequest(models.Model):
    from_user: User = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="request_from_user"
    )
    to_user: User = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="request_to_user"
    )
    message: str = models.CharField(max_length=255)
    accepted: bool = models.BooleanField(default=False)
    created_at: datetime = models.DateTimeField(auto_now_add=True)
    updated_at: datetime = models.DateField(auto_now=True)
    seen_at: datetime = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"User #{self.from_user} sent request to #{self.to_user}"

    @staticmethod
    def check_friend_request(user1, user2):
        return FriendRequest.objects.filter(
            Q(from_user=user1, to_user=user2) | Q(from_user=user2, to_user=user1)
        ).exists()

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.from_user == self.to_user:
            raise ValidationError("Users cannot send requests to themselves.")
        if not self.id:
            if self.check_friend_request(self.from_user, self.to_user):
                raise ValidationError("request already exists.")

        super(FriendRequest, self).save(*args, **kwargs)


class BlockedUser(models.Model):
    user: User = models.ForeignKey(User, on_delete=models.CASCADE)
    blocked_users = models.ManyToManyField(
        User, blank=True, related_name="blocked_by_users"
    )

    def __str__(self):
        return self.user.username


class CelebVerification(models.Model):
    user: User = models.ForeignKey(User, on_delete=models.CASCADE)

    REQUESTED = "rq"
    DECLINED = "dc"
    ACCEPTED = "ac"
    STATUS_CHOICES = (
        (REQUESTED, "Requested"),
        (DECLINED, "Declined"),
        (ACCEPTED, "Accepted"),
    )

    status: str = models.CharField(
        max_length=2, choices=STATUS_CHOICES, default=REQUESTED
    )

    category: str = models.CharField(max_length=2, choices=User.CATEGORY_CHOICES)

    timestamp: datetime = models.DateTimeField(auto_now_add=True)
    updated: datetime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.status}"

    @property
    def status_verbose(self):
        return dict(CelebVerification.STATUS_CHOICES)[self.status]

    @property
    def category_verbose(self):
        return dict(User.CATEGORY_CHOICES)[self.category]
