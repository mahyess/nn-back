from django.urls import path
from .views import (
    ChatList,
    init_message,
    create_group_message,
    get_group_chat_details,
    leave_group_chat,
    add_participants_gm,
    remove_participants_gm,
    add_message_attachment,
    message_gallery,
    message_links,
)

urlpatterns = [
    path("", ChatList.as_view()),
    path("init-message/", init_message),
    path("group/create/", create_group_message),
    path("group/add-participants/", add_participants_gm),
    path("group/remove-participants/", remove_participants_gm),
    path("group/<str:gid>/", get_group_chat_details),
    path("group/<str:gid>/leave/", leave_group_chat),
    path("<str:gid>/attachments/", add_message_attachment),
    path("<str:gid>/gallery/", message_gallery),
    path("<str:gid>/links/", message_links),
]
