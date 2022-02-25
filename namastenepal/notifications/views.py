from asgiref.sync import async_to_sync
from django.shortcuts import render

# Create your views here.
from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.views import APIView

from namastenepal.channels_app.signals import send_notification
from namastenepal.community.utils import start_new_thread
from namastenepal.notifications.models import Notification
from namastenepal.notifications.serializers import NotificationSerializer


class NotificationPagination(pagination.PageNumberPagination):
    page_size = 15


class NotificationsAPI(APIView):
    _paginator: NotificationPagination

    serializer_class = NotificationSerializer
    pagination_class = NotificationPagination

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by(
            "-timestamp"
        )

    def get(self, request):
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)


class NotificationMarkRead(APIView):
    @staticmethod
    def get(request):
        Notification.objects.filter(user=request.user).exclude(seen=True).update(
            seen=True
        )

        return Response(
            data={"success": "all notifications marked as read."}, status=200
        )


@start_new_thread
def create_notification(action, post_user, from_user, post):
    ins, created = Notification.objects.update_or_create(
        user=post_user,
        from_user=from_user,
        post_notification__post=post,
        defaults={"action": action},
    )
    if created:
        async_to_sync(send_notification)(
            username=str(post_user.username), data=NotificationSerializer(ins).data
        )
    return True
