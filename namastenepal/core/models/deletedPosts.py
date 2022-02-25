from django.db import models
from namastenepal.core.models import User

class DeletedPost(models.Model):
    pid = models.CharField(max_length=100, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    user = models.CharField(max_length=255)
    title = models.CharField(max_length=150)
    body = models.TextField(blank=True)
    media = models.FileField(null=True, blank=True)
    likes = models.ManyToManyField(User, blank=True, related_name="deleted_posts_likes")
    total_likes = models.FloatField(default=0.00)
    reports = models.ManyToManyField(
        User, blank=True, related_name="deleted_posts_reports")
    timestamp = models.DateTimeField(auto_now_add=True)
    total_reports = models.FloatField(default=0.00)

    def __str__(self):
        return str(self.title)
