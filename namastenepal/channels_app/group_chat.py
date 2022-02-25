"""group chat"""
import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework.generics import get_object_or_404

from namastenepal.chat_messages.models import Message, ChatUsersGroup
from .signals import send_new_message
from ..chat_messages.serializers import MessageSerializer
from ..common import UUIDEncoder


class GroupChatConsumer(AsyncWebsocketConsumer):
    """group chat consumer"""

    room_group_name: str

    async def connect(self):
        if self.scope["user"].is_authenticated:
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, *args):
        # leave group room
        print("disconnected. . ")
        if "room_groupMessage_id" in self.scope["session"]:
            room_group_name = f"namastenepal_group_chat_{self.scope['session']['room_groupMessage_id']}"
            await self.channel_layer.group_discard(room_group_name, self.channel_name)
        else:
            await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        if data["command"] in self.commands:
            await getattr(self, data["command"])(data)
        else:
            await self.send_message({"error": "Command not found."})

    async def init_chat(self, data):
        """init chat"""
        group_id = data["groupID"]
        content = {"command": "init_chat"}

        if not group_id:
            content["error"] = "Unable to get group: " + str(group_id)
            await self.send_message(content)
        else:
            group = await database_sync_to_async(get_object_or_404)(
                ChatUsersGroup, id=group_id
            )

            # if 'room_groupMessage_id' in self.scope['session']:
            #     if self.scope['session']['room_groupMessage_id'] == str(group.id):
            #         pass
            #     else:
            #         del self.scope['session']['room_groupMessage_id']

            self.scope["session"]["room_groupMessage_id"] = str(group.id)
            self.scope["session"].save()

            content["success"] = "Chatting in with success group"
            await self.send_message(content)

    @staticmethod
    @database_sync_to_async
    def get_last_messages_and_unread_count(_user, _group_id, page_node=None):
        """get_last_messages_and_unread_count"""
        conversation = Message.objects.filter(group__id=_group_id).order_by(
            "-created_at"
        )
        unread = conversation.exclude(author=_user, seen=True).count()
        if page_node:
            conversation = conversation.filter(created_at__lt=page_node)
        return conversation[:50], unread

    async def fetch_messages(self, data):
        """fetch messages"""
        _group_id = data["groupID"]
        _user = self.scope["user"]
        messages, unread = await self.get_last_messages_and_unread_count(
            _user, _group_id
        )

        await self.send_message(
            {
                "command": "messages",
                "messages": MessageSerializer(messages, many=True).data,
                "unread_count": unread,
            }
        )

    @staticmethod
    @database_sync_to_async
    def get_last_message_with_attachment(_group_id, author, content):
        """get last message with attachment"""
        return Message.objects.filter(
            group__id=_group_id,
            author=author,
            content=content,
        ).order_by("-created_at")[0]

    async def new_message(self, data):
        """new message"""
        _group_id = data["groupID"]
        author_user = self.scope["user"]
        text = data["content"]

        if text[:15] == "[[ATTACHMENT]]:":
            message = await self.get_last_message_with_attachment(
                _group_id, author_user, text
            )
        else:
            message = await database_sync_to_async(Message.objects.create)(
                author=author_user, content=text, group_id=_group_id
            )

        group = await database_sync_to_async(ChatUsersGroup.objects.get)(id=_group_id)

        for user in group.participants.all():
            if user != author_user:
                await send_new_message(user.username, MessageSerializer(message).data)
                # send_fcm_push_notification(
                # "Namaste Nepal: " + author_user.username,
                # text,
                # user.username)
        from namastenepal.chat_messages.serializers import MessageCardSerializer

        await self.send_chat_message(
            {
                "command": "new_message",
                "group": _group_id,
                "message": MessageSerializer(message).data,
            }
        )

    @staticmethod
    @database_sync_to_async
    def set_messages_to_read(group_id, user):
        """get last message with attachment"""
        Message.objects.filter(group__id=group_id, seen=False,).exclude(
            author=user
        ).update(seen=True)
        return True

    async def read_messages(self, data):
        group_id = data["groupID"]
        user = self.scope["user"]

        await self.set_messages_to_read(group_id, user)

        await self.send_message(
            {
                "command": "read_messages",
                "group": group_id,
                "message": "messages set to read",
            }
        )

    commands = {
        "init_chat": init_chat,
        "fetch_messages": fetch_messages,
        "new_message": new_message,
        "read_messages": read_messages,
    }

    async def send_message(self, message):
        """send message"""
        await self.send(text_data=json.dumps(message, cls=UUIDEncoder))

    async def send_chat_message(self, message):
        """send chat message"""
        group = message.get("group")

        self.scope["session"]["room_groupMessage_id"] = group
        self.scope["session"].save()

        self.room_group_name = "namastenepal_group_chat_{0}".format(group)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # channel_layer = get_channel_layer()
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    async def chat_message(self, event):
        """Receive message from room group"""
        message = event["message"]
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message, cls=UUIDEncoder))
