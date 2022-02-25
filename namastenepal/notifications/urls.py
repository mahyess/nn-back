from django.urls import path

from .views import (
    NotificationsAPI,
    NotificationMarkRead,
)

urlpatterns = [
    path("", NotificationsAPI.as_view(), name="all-notifications"),
    path("mark-all-as-read/", NotificationMarkRead.as_view()),
]
