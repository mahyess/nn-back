from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import (
    ChatUsersGroup,
    Message,
    ChatUsersGroupProfile,
)
from .serializers import (
    MessageUsersGroupCardSerializer,
    MessageSerializer,
    MessageUsersGroupDetailsSerializer,
)
from namastenepal.common import get_object_or_404, get_exact_match
from namastenepal.core.models import User


class ChatListPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 10000


class ChatList(generics.ListAPIView):
    serializer_class = MessageUsersGroupCardSerializer
    pagination_class = ChatListPagination

    def get_queryset(self):
        requesting_user: User = self.request.user
        return (
            ChatUsersGroup.objects.filter(participants__pk=requesting_user.pk)
                .order_by("-latest_activity")
                .distinct()
        )


@api_view(["GET"])
def get_group_chat_details(request, gid):
    group_chat = get_object_or_404(
        {"gid", f"chat with gid {gid} not found."}, ChatUsersGroup, id=gid
    )

    return Response(
        MessageUsersGroupDetailsSerializer(
            group_chat, context={"request": request}
        ).data,
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def init_message(request):
    username = request.data.get("username")

    message_to = get_object_or_404(
        {"username": f"User with username: {username} not found."},
        get_user_model(),
        username=username,
    )

    message_user_group, is_created = get_exact_match(
        ChatUsersGroup, "participants", [request.user.id, message_to.id]
    ).get_or_create(defaults={})

    if is_created:
        message_user_group.participants.set([request.user, message_to])

    return Response(
        MessageUsersGroupCardSerializer(
            message_user_group,
            context={"request": request},
        ).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def create_group_message(request):
    group_name = request.data.get("groupName", "Untitled Group")
    participants = request.data.get("participants")
    if not participants:
        return Response(
            {"error": "participants are required"}, status=status.HTTP_400_BAD_REQUEST
        )

    participants = participants.split(",")

    try:
        participants = [
            request.user,
            *[
                get_user_model().objects.get(username=user.strip())
                for user in participants
            ],
        ]
    except User.DoesNotExist:
        raise ValidationError(
            detail={"participants": "User not found with username provided"},
            code=status.HTTP_400_BAD_REQUEST,
        )

    group_profile = ChatUsersGroupProfile.objects.create(
        admin=request.user, name=group_name, user_group=ChatUsersGroup.objects.create()
    )
    group_profile.user_group.participants.set(participants)

    return Response(
        MessageUsersGroupCardSerializer(group_profile.user_group).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def add_participants_gm(request):
    errors = {}

    requesting_user: User = request.user
    group_id = request.data.get("groupID")
    if not group_id:
        errors["groupID"] = "groupID required"

    participants = request.data.get("participants")
    if not participants:
        errors["participants"] = "participants required"

    if len(errors):
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    group = get_object_or_404(
        {"groupID": f"user group with id {group_id} not found"},
        ChatUsersGroup,
        id=group_id,
    )

    participants = participants.split(",")
    try:
        participants = [
            *list(group.participants.all()),
            *[
                get_user_model().objects.get(username=user.strip())
                for user in participants
            ],
        ]
    except User.DoesNotExist:
        raise ValidationError(
            detail={"participants": "User not found with username provided"},
            code=status.HTTP_400_BAD_REQUEST,
        )

    if hasattr(group, "group_profile"):
        if requesting_user.uid != group.admin.uid:
            return Response(
                {"error": "Only admin can add/remove participants"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        group.participants.set(participants)
        success_message = "participant added"
    else:
        group_profile = ChatUsersGroupProfile.objects.create(
            admin=request.user, user_group=ChatUsersGroup.objects.create()
        )
        group_profile.user_group.participants.set(participants)
        group = group_profile.user_group
        success_message = "new group created"

    serializer = MessageUsersGroupCardSerializer(group)
    return Response(
        {"success": success_message, "data": serializer.data},
        status=status.HTTP_201_CREATED,
    )


@api_view(["POST"])
def remove_participants_gm(request):
    errors = {}

    group_id = request.data.get("groupID")
    if not group_id:
        errors["groupID"] = "groupID required"

    participant = request.data.get("participant")
    if not participant:
        errors["participant"] = "participant required"

    if len(errors):
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)

    group = get_object_or_404(
        {"groupID": f"user group with id {group_id} not found"},
        ChatUsersGroup,
        id=group_id,
    )

    requesting_user: User = request.user
    if not hasattr(group, "group_profile"):
        raise ValidationError(
            detail={"group": "group with id provided is not a group chat"}
        )

    if requesting_user.uid != group.group_profile.admin.uid:
        return Response(
            {"error": "Only admin can add/remove participants"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if participant == group.group_profile.admin.username:
        return Response(
            {"error": "Cannot remove admin"}, status=status.HTTP_401_UNAUTHORIZED
        )

    group.participants.remove(
        get_object_or_404(
            {"user": f"user with username {participant} not found"},
            User,
            username=participant,
        )
    )

    serializer = MessageUsersGroupCardSerializer(group)
    return Response(
        {"success": "participant removed", "data": serializer.data},
        status=status.HTTP_200_OK,
    )


@api_view(["DELETE"])
def leave_group_chat(request, gid):
    requesting_user: User = request.user
    group = get_object_or_404(
        {"gid": f"User group with gid: {gid} not found"}, ChatUsersGroup, id=gid
    )
    if hasattr(group, "group_profile"):
        group.participants.remove(requesting_user)

        return Response({"success": "Group left"}, status=status.HTTP_200_OK)

    return Response(
        {"error": "only group chats can be left"},
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST"])
def add_message_attachment(request, gid):
    data = {
        "author": request.user.pk,
        "group": get_object_or_404(
            {"group": f"user group with gid: {gid} not found"},
            ChatUsersGroup,
            id=gid,
        ).pk,
        "content": "attachment",
    }
    attachment = request.data.get("attachment", None)
    if attachment:
        kind = attachment.content_type

        if "image" in kind:
            attachment_type = "image"
        elif "video" in kind:
            attachment_type = "video"
        else:
            return Response(
                data={"media": "Only video/image file is supported for now."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data["attachment"] = attachment

        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            message_instance = serializer.save()
            message_instance.content = f"[[ATTACHMENT]]:[[{attachment_type.upper()}]]:{message_instance.attachment.url}"
            message_instance.save()

            return Response(
                {
                    "msg": "Success",
                    "instance": MessageSerializer(message_instance).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {"msg": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "msg": "error",
            "errors": {
                "attachment": "Attachment can not be blank if posted without websocket"
            },
        },
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
def message_gallery(request, gid):
    gallery_list = Message.objects.filter(
        Q(content__istartswith="[[ATTACHMENT]]:[[IMAGE]]")
        | Q(content__istartswith="[[ATTACHMENT]]:[[VIDEO]]"),
        group__id=gid,
    ).values_list("content", flat=True)

    return Response({"gallery": list(gallery_list)}, status=status.HTTP_200_OK)


@api_view(["GET"])
def message_links(request, gid):
    links_list = Message.objects.filter(
        group__id=gid,
        content__iregex=r"(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.["
                        r"a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?://(?:www\.|(?!www))[a-zA-Z0-9]+\.["
                        r"^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})",
    ).values_list("content", flat=True)

    return Response({"links": list(links_list)}, status=status.HTTP_200_OK)
