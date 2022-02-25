"""notification"""
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from namastenepal.chat_messages.models import Message
from namastenepal.notifications.models import Notification
from namastenepal.notifications.serializers import NotificationSerializer
from namastenepal.usermodule.models import FriendRequest


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    """notification consumer"""

    room_name: str
    user_name: str
    room_group_name: str

    async def connect(self):
        """connect"""
        self.room_name = "notification"
        user = self.scope["user"]
        self.user_name = user.username
        self.room_group_name = f"namastenepal_{self.room_name}_{self.user_name}"
        # Join room group

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        if self.scope["user"].is_authenticated:
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, _):
        """leave group room"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def notifications(self, event):
        """notifications"""
        await self.send_json(event)

    async def receive(self, **kwargs):
        """receive"""
        text_data = kwargs.pop("text_data")

        data = json.loads(text_data)
        await getattr(self, data["command"])()

    async def fetch_notification(self):
        """fetch notification"""
        user = self.scope["user"]
        notifications = Notification.objects.filter(user=user).order_by("-timestamp")
        serializer = NotificationSerializer(notifications, many=True)

        await self.send_json(
            {"command": "notifications", "notifications": serializer.data}
        )

    async def fetch_unread_messages(self):
        """message unread count"""
        user = self.scope["user"]
        unread = (
            Message.objects.filter(group__participants=user)
            .exclude(author=user)
            .count()
        )

        await self.send_json({"command": "unread_messages", "count": unread})

    async def fetch_friend_request(self):
        """fetch requests count"""
        user = self.scope["user"]
        all_requests_count = FriendRequest.objects.filter(
            to_user__username=user, accepted=False
        ).count()
        unseen_requests_count = FriendRequest.objects.filter(
            to_user__username=user, accepted=False, seen_at__isnull=True
        ).count()

        await self.send_json(
            {
                "command": "fetch_requests",
                "all_requests_count": all_requests_count,
                "unseen_requests_count": unseen_requests_count,
            }
        )

    commands = {
        "fetch_notification": fetch_notification,
        "fetch_unread_messages": fetch_unread_messages,
        "fetch_friend_request": fetch_friend_request,
    }
