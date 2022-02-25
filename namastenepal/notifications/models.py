from django.conf import settings
from django.db import models

# Create your models here.
from namastenepal.community.models import Community
from namastenepal.core.models import User
from namastenepal.posts.models import Post, Comment


class Notification(models.Model):
    user: User = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="receiver",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sender"
    )

    POST = "p"
    COMMENT = "c"
    COMMUNITY = "s"
    FRIEND = "f"
    CATEGORY_CHOICES = (
        (POST, "Post"),
        (COMMENT, "Comment"),
        (COMMUNITY, "Community"),
        (FRIEND, "Friend"),
    )
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, null=True)

    action = models.CharField(max_length=255)
    seen = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user.username)

    @property
    def category_verbose(self):
        return dict(Notification.CATEGORY_CHOICES)[self.category]


class PostNotification(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_notifications"
    )
    notification = models.OneToOneField(
        Notification, on_delete=models.CASCADE, related_name="post_notification"
    )

    TAG = "t"
    LIKE = "l"
    SUGGESTION = "s"
    REMOVED = "r"
    CATEGORY_CHOICES = (
        (TAG, "Tag"),
        (LIKE, "Like"),
        (SUGGESTION, "Suggestion"),
        (REMOVED, "Removed"),
    )
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default=LIKE)

    @property
    def category_verbose(self):
        return dict(PostNotification.CATEGORY_CHOICES)[self.category]


class CommentNotification(models.Model):
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, related_name="comment_notifications"
    )
    notification = models.OneToOneField(
        Notification, on_delete=models.CASCADE, related_name="comment_notification"
    )

    COMMENT = "c"
    REPLY = "r"
    MENTION = "m"
    UPVOTE = "u"
    CATEGORY_CHOICES = (
        (COMMENT, "Tag"),
        (REPLY, "Reply"),
        (MENTION, "Mention"),
        (UPVOTE, "Upvote"),
    )
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default=COMMENT)

    @property
    def category_verbose(self):
        return dict(CommentNotification.CATEGORY_CHOICES)[self.category]


class CommunityNotification(models.Model):
    community = models.ForeignKey(
        Community, on_delete=models.CASCADE, related_name="community_notifications"
    )
    notification = models.OneToOneField(
        Notification, on_delete=models.CASCADE, related_name="community_notification"
    )

    JOIN_REQUEST = "j"
    REQUEST_ACCEPT = "r"
    CATEGORY_CHOICES = (
        (JOIN_REQUEST, "Join Request"),
        (REQUEST_ACCEPT, "Request Accept"),
    )
    category = models.CharField(
        max_length=1, choices=CATEGORY_CHOICES, default=REQUEST_ACCEPT
    )

    @property
    def category_verbose(self):
        return dict(CommunityNotification.CATEGORY_CHOICES)[self.category]


class FriendNotification(models.Model):
    friend = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friend_notifications",
    )
    notification = models.OneToOneField(
        Notification, on_delete=models.CASCADE, related_name="friend_notification"
    )

    REQUEST_ACCEPT = "r"
    CATEGORY_CHOICES = ((REQUEST_ACCEPT, "Request Accept"),)
    category = models.CharField(
        max_length=1, choices=CATEGORY_CHOICES, default=REQUEST_ACCEPT
    )

    @property
    def category_verbose(self):
        return dict(FriendNotification.CATEGORY_CHOICES)[self.category]
