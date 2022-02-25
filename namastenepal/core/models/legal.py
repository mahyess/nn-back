from django.db import models


class Term(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)


class PrivacyPolicy(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)


class StoragePolicy(models.Model):
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now=True)
    updated = models.DateTimeField(auto_now_add=True)
