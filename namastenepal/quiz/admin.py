from django.contrib import admin
from .models import *


class QuizAdmin(admin.ModelAdmin):
    list_display = ['question', 'is_published', 'timestamp']

admin.site.register(Quiz, QuizAdmin)
admin.site.register(QuizAnswer)
