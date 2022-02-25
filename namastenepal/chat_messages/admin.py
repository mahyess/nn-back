from django.contrib import admin

from .models import (
    Message,
    ChatUsersGroup,
    ChatUsersGroupProfile,
)


class RecentMessageAdmin(admin.ModelAdmin):
    list_display = ["author", "group", "content"]


admin.site.register(Message)
admin.site.register(ChatUsersGroup)
admin.site.register(ChatUsersGroupProfile)
