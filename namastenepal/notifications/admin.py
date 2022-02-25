from django.contrib import admin
from django_reverse_admin import ReverseModelAdmin

# Register your models here.
from .models import (
    Notification,
    PostNotification,
    CommentNotification,
    CommunityNotification,
    FriendNotification,
)


class ReverseModelAdminNotificationBase(ReverseModelAdmin):
    list_display = (
        "id",
        "__str__",
    )
    list_filter = ("category",)
    inline_type = "stacked"
    inline_reverse = ["notification"]


class PostNotificationAdmin(ReverseModelAdminNotificationBase):
    pass


class CommentNotificationAdmin(ReverseModelAdminNotificationBase):
    pass


class CommunityNotificationAdmin(ReverseModelAdminNotificationBase):
    pass


class FriendNotificationAdmin(ReverseModelAdminNotificationBase):
    pass


admin.site.register(Notification)
admin.site.register(PostNotification, PostNotificationAdmin)
admin.site.register(CommentNotification, CommentNotificationAdmin)
admin.site.register(CommunityNotification, CommunityNotificationAdmin)
admin.site.register(FriendNotification, FriendNotificationAdmin)
