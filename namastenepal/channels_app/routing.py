"""routing"""
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from namastenepal.channels_app.group_chat import GroupChatConsumer
from namastenepal.channels_app.notification import NotificationConsumer
from namastenepal.channels_app.token_auth import TokenAuthMiddlewareStack
from namastenepal.channels_app.user_channels import UserConsumer

websocket_urlpatterns = [
    # url(r"^ws/chat$", consumers.ChatConsumer),
    path("ws/chat/", GroupChatConsumer),
    path("ws/notification/", NotificationConsumer),
    path("ws/user/", UserConsumer),
]
 
application = ProtocolTypeRouter(
    {
        "websocket": TokenAuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
    }
)
