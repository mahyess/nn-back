from django.db import models


class Gender(models.Model):
    title = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return self.title
