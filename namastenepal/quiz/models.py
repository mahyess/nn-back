from django.db import models
from namastenepal.core.models import User


class Quiz(models.Model):
    question = models.CharField(max_length=200)
    ans_1 = models.CharField(max_length=200)
    ans_2 = models.CharField(max_length=200)
    ans_3 = models.CharField(max_length=200)
    ans_4 = models.CharField(max_length=200)
    is_published = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question


class QuizAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.CharField(max_length=10)
    is_correct = models.BooleanField(default=False)
    answered_in = models.FloatField(default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
