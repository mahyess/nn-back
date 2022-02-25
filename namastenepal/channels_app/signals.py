"""async signals"""
import json
import requests
from channels.layers import get_channel_layer

from firebase.models import Token
from namastenepal.community.utils import start_new_thread


async def send_notification(username, data):
    """send notification"""
    channel_layer = get_channel_layer()
    group_name = f"namastenepal_notification_{username}"
    await channel_layer.group_send(
        group_name,
        {"type": "notifications", "command": "notifications", "notifications": [data]},
    )


async def send_unread_notification(username, count):
    """send unread notification"""
    channel_layer = get_channel_layer()
    group_name = f"namastenepal_notification_{username}"
    await channel_layer.group_send(
        group_name,
        {"type": "notifications", "command": "unread_notifications", "count": count},
    )


async def send_message_unread(payload, unread):
    """send message unread"""
    channel_layer = get_channel_layer()
    group_name = f"namastenepal_notification_{payload}"
    await channel_layer.group_send(
        group_name,
        {"type": "notifications", "command": "unread_messages", "count": unread},
    )


async def send_new_message(payload, message):
    """send new message"""
    channel_layer = get_channel_layer()
    group_name = f"namastenepal_notification_{payload}"
    await channel_layer.group_send(
        group_name,
        {"type": "notifications", "command": "new_message", "message": message},
    )


async def send_recent_message(payload, message):
    """send recent message"""
    channel_layer = get_channel_layer()
    group_name = f"namastenepal_chat_{payload}"
    await channel_layer.group_send(
        group_name,
        {"type": "chat_message", "command": "fetch_recent", "message": message},
    )


async def read_messages(payload, message):
    """read messages"""
    channel_layer = get_channel_layer()
    group_name = f"namastenepal_chat_{payload}"
    await channel_layer.group_send(
        group_name,
        {"type": "read_messages", "command": "read_messages", "message": message},
    )


async def send_friend_request(username, request):
    """send friend request"""
    channel_layer = get_channel_layer()
    group_name = f"namastenepal_notification_{username}"
    await channel_layer.group_send(
        group_name,
        {"type": "notifications", "command": "new_request", "request": request},
    )


async def send_friend_request_count(user, all_requests_count, unseen_requests_count):
    """send friend request count"""
    channel_layer = get_channel_layer()
    group_name = f"namastenepal_user_channels_{user.username}"
    await channel_layer.group_send(
        group_name,
        {
            "type": "friend_requests",
            "command": "fetch_requests_count",
            "all_requests_count": all_requests_count,
            "unseen_requests_count": unseen_requests_count,
        },
    )


@start_new_thread
def send_fcm_push_notification(title, body, user):
    """
    send notification
    # deprecated
    """
    tokens = Token.objects.filter(user__username=user)

    if tokens.exists():
        data = json.dumps(
            {
                "notification": {
                    "title": title,
                    "body": body,
                    "icon": "https://www.namastenepal.com/static/img/icons/namaste.png",
                    "click_action": "https://www.namastenepal.com",
                },
                "to": [ins.token for ins in tokens],
            }
        )

        headers = {
            "content-type": "application/json",
            "Authorization": "key=AAAAtRJ4Hno:APA91bG-ZQ0V6_IZh0-7MqqD2wiYkkpC_CHd2pWrJYEd_"
            "LtPyxsQ1vPIu3tYn0mua7pgEOgegfkWRg8NNsmrVwwaVvmZZtgiqSRCBtU63Lh5e1z-"
            "DIFqnWhmYpLwv9yuNERhglzzwD8l",
        }
        req = requests.post(
            "https://fcm.googleapis.com/fcm/send", data=data, headers=headers
        )
        return req
