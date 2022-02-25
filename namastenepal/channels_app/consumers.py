# """consumers"""
# import json
#
# from channels.db import database_sync_to_async
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.db.models import Q
# from django.shortcuts import get_object_or_404
#
# from namastenepal.chat_messages.models import Message, MessageUsersGroup
# from namastenepal.core.models.user import User
# from .signals import (
#     send_message_unread,
#     send_new_message,
#     send_fcm_push_notification,
#     read_messages,
# )
#
#
# class ChatConsumer(AsyncWebsocketConsumer):
#     """chat consumer"""
#
#     room_group_name: str
#
#     async def connect(self):
#         if self.scope["user"].is_authenticated:
#             await self.accept()
#         else:
#             await self.close()
#
#     async def disconnect(self, *args):
#         """leave group room"""
#         print("disconnected... ")
#         if "room_group_id" in self.scope["session"]:
#             room_group_name = "namastenepal_chat_{0}".format(
#                 self.scope["session"]["room_group_id"]
#             )
#             await self.channel_layer.group_discard(room_group_name, self.channel_name)
#         else:
#             await self.close()
#
#     async def receive(self, text_data=None, _=None):
#         data = json.loads(text_data)
#         if data["command"] in self.commands:
#             await getattr(self, data["command"])(data)
#             # if data['command'] in self.commands:
#             # await self.commands[data['command']](self, data)
#         else:
#             content = {"error": "Command not found."}
#             await self.send_message(content)
#
#     @staticmethod
#     @database_sync_to_async
#     def get_or_create_message_user_group(user1, user2):
#         """get message user group model if exists, else create one"""
#         group, _ = MessageUsersGroup.objects.filter(
#             Q(user1=user1, user2=user2) | Q(user1=user2, user2=user1)
#         ).get_or_create(defaults={"user1": user1, "user2": user2})
#         return group
#
#     async def init_chat(self, data):
#         """init chat"""
#         to_user = data["username"]
#         from_user = self.scope["user"]
#         content = {"command": "init_chat"}
#
#         to_user = await database_sync_to_async(get_object_or_404)(
#             User, username=to_user
#         )
#         if not to_user:
#             content["error"] = f"Unable to get User with username: {str(to_user)}"
#             await self.send_message(content)
#         else:
#             group = await self.get_or_create_message_user_group(from_user, to_user)
#
#             self.scope["session"]["room_group_id"] = group.gid
#             self.scope["session"].save()
#
#             content["success"] = "Chatting in with success group"
#             await self.send_message(content)
#
#     @staticmethod
#     @database_sync_to_async
#     def get_last_messages_and_unread_count(_user, _friend, page_node=None):
#         """get last messages and unread count"""
#         conversation = Message.objects.filter(
#             Q(author=_user, message_to=_friend) | Q(author=_friend, message_to=_user)
#         ).order_by("-created_at")
#         unread = conversation.filter(message_to=_user, seen=False).count()
#         if page_node:
#             conversation = conversation.filter(created_at__lt=page_node)
#         return conversation[:50], unread
#
#     @staticmethod
#     @database_sync_to_async
#     def get_user_by_username(username):
#         """get user by username"""
#         return User.objects.get(username=username)
#
#     @staticmethod
#     @database_sync_to_async
#     def set_messages_to_read(_user, _friend=None, _messages=None):
#         """"set messages to read"""
#         if _messages:
#             Message.objects.filter(id__in=_messages, seen=False).update(seen=True)
#         elif _friend:
#             Message.objects.filter(author=_friend, message_to=_user, seen=False).update(
#                 seen=True
#             )
#         else:
#             pass
#
#     async def fetch_messages(self, data):
#         """fetch messages"""
#         if data.get("username"):
#             _user = self.scope["user"]
#             _friend = await self.get_user_by_username(data.get("username"))
#             messages, unread = await self.get_last_messages_and_unread_count(
#                 _user, _friend
#             )
#
#             await send_message_unread(_user.username, unread)
#             await self.send_message(
#                 {
#                     "command": "messages",
#                     "messages": self.messages_to_json(messages),
#                     "status_code": 200,
#                 }
#             )
#             await self.set_messages_to_read(_user=self.scope["user"], _friend=_friend)
#         else:
#             await self.send_message(
#                 {
#                     "command": "messages",
#                     "error": "no friend selected",
#                     "status_code": 400,
#                 }
#             )
#
#     @staticmethod
#     @database_sync_to_async
#     def get_last_message_with_attachment(author, content, message_to):
#         """get last message with attachment"""
#         return (
#             Message.objects.filter(
#                 Q(author=author, message_to=message_to)
#                 | Q(author=message_to, message_to=author),
#                 content=content,
#             )
#             .order_by("-created_at")
#             .first()
#         )
#
#     async def new_message(self, data):
#         """when new message is sent"""
#         text = data["content"]
#         author_user = self.scope["user"]
#         to_user = await self.get_user_by_username(data["to"])
#         if text[:15] == "[[ATTACHMENT]]:":
#             message = await self.get_last_message_with_attachment(
#                 author_user, text, to_user
#             )
#         else:
#             message = await database_sync_to_async(Message.objects.create)(
#                 author=author_user, content=text, message_to=to_user
#             )
#
#         await send_new_message(to_user.username, self.message_to_json(message))
#         _ = send_fcm_push_notification(
#             "Namaste Nepal: " + author_user.username, text, to_user.username
#         )
#
#         await self.send_chat_message(
#             {
#                 "command": "new_message",
#                 "to_user": to_user.username,
#                 "message": self.message_to_json(message),
#             }
#         )
#
#     async def read_messages(self, data):
#         """read messages"""
#         if data["from"]:
#             _friend = await self.get_user_by_username(data["from"])
#             await self.set_messages_to_read(_user=self.scope["user"], _friend=_friend)
#         elif data["messages"]:
#             await self.set_messages_to_read(
#                 _user=self.scope["user"], _messages=data["messages"]
#             )
#         await read_messages(self.scope["user"].username, {"msg": "messages read"})
#
#     commands = {
#         "init_chat": init_chat,
#         "fetch_messages": fetch_messages,
#         "new_message": new_message,
#         "read_messages": read_messages,
#     }
#
#     def messages_to_json(self, messages):
#         """array"""
#         return [self.message_to_json(message) for message in messages]
#
#     @staticmethod
#     def message_to_json(message):
#         """convert django model instance to json"""
#         return {
#             "id": str(message.id),
#             "from": message.author.username,
#             "to": message.message_to.username,
#             "content": message.content,
#             "seen": message.seen,
#             "created_at": str(message.created_at),
#         }
#
#     def friends_to_json(self, friends):
#         """array"""
#         return [self.friend_to_json(friend) for friend in friends]
#
#     @staticmethod
#     def friend_to_json(friend):
#         """convert django model instance to json"""
#         to_return = {
#             "id": friend.id,
#             "friend_username": friend.to_user.username,
#             "friend_profile_pic": str(friend.to_user.profile.avatar.url),
#         }
#         if friend.recent_message:
#             to_return = {
#                 **to_return,
#                 "recent_message_seen": friend.recent_message.get("seen"),
#                 "recent_message_content": friend.recent_message.get("content"),
#                 "recent_message_created_at": friend.recent_message.get("created_at"),
#             }
#         else:
#             to_return = {
#                 **to_return,
#                 "recent_message_seen": False,
#                 "recent_message_content": "No messages yet.",
#                 "recent_message_created_at": None,
#             }
#         return to_return
#
#     async def send_message(self, message):
#         """send message"""
#         await self.send(text_data=json.dumps(message))
#
#     async def send_chat_message(self, message):
#         """send chat message"""
#         from_user = self.scope["user"]
#         to_user = await self.get_user_by_username(message.get("to_user"))
#
#         group = await self.get_or_create_message_user_group(to_user, from_user)
#         # Send message to room group
#
#         self.scope["session"]["room_group_id"] = group.gid
#         self.scope["session"].save()
#
#         self.room_group_name = f"namastenepal_chat_{str(group.gid)}"
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#
#         # channel_layer = get_channel_layer()
#         await self.channel_layer.group_send(
#             self.room_group_name, {"type": "chat_message", "message": message}
#         )
#
#     async def chat_message(self, event):
#         """Receive message from room group"""
#         message = event["message"]
#         # Send message to WebSocket
#         await self.send(text_data=json.dumps(message))
