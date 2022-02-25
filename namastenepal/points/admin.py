from django.contrib import admin
from .models import Point, Badge

myModels = [Point, Badge]
admin.site.register(myModels)
