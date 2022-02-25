from django.urls import path
from .views import add_new_firebase_token

urlpatterns = [
    path("add-new-token", add_new_firebase_token),
]
