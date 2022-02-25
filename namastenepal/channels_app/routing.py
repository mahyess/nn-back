"""routing"""
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url

from namastenepal.channels_app.token_auth import TokenAuthMiddlewareStack
from . import (
    # consumers,
    notification,
    user_channels,
    group_chat,
)

websocket_urlpatterns = [
    # url(r"^ws/chat$", consumers.ChatConsumer),
    url(r"^ws/chat$", group_chat.GroupChatConsumer),
    url(r"^ws/notification$", notification.NotificationConsumer),
    url(r"^ws/user$", user_channels.UserConsumer),
]

application = ProtocolTypeRouter(
    {
        "websocket": TokenAuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
