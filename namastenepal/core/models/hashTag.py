from django.db import models


class HashTag(models.Model):
    title = models.CharField(max_length=20, unique=True)

    REQUIRED_FIELDS = ['title']

    def __str__(self):
        return self.title
