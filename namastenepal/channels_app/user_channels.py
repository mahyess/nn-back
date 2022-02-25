"""user channels"""
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from namastenepal.usermodule.models import FriendRequest
from namastenepal.usermodule.serializers import ReceivedFriendRequestSerializer


class UserConsumer(AsyncJsonWebsocketConsumer):
    """user consumer"""

    room_name: str
    user_name: str
    room_group_name: str

    async def connect(self):
        """connect"""

        self.room_name = "user_channels"
        user = self.scope["user"]
        self.user_name = user.username
        self.room_group_name = f"namastenepal_{self.room_name}_{self.user_name}"
        # Join room group

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        if self.scope["user"].is_authenticated:
            await self.accept()

    async def disconnect(self, _):
        """leave group room"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, **kwargs):
        """receive"""
        text_data = kwargs.pop("text_data")
        data = json.loads(text_data)
        await getattr(self, data["command"])()

    async def fetch_requests_count(self):
        """fetch requests"""
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
        "fetch_requests_count": fetch_requests_count,
    }
