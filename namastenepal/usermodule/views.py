from asgiref.sync import async_to_sync
from django.conf import settings
from django.db import transaction
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.utils import timezone
from rest_framework import pagination, generics
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.views import APIView

from namastenepal.channels_app.signals import (
    send_friend_request_count,
    send_friend_request,
)
from namastenepal.core.models import User
from namastenepal.points.models import Point
from namastenepal.points.serializers import PointSerializer
from .models import AuditLogs, Friend, Profile, FriendRequest, BlockedUser
from .models import CelebVerification
from .serializers import (
    AuditLogSerializer,
    FriendsSerializer,
    UserSerializer,
    ReceivedFriendRequestSerializer,
    SentFriendRequestSerializer,
    AvatarImageSerializer,
    CoverImageSerializer,
    UserProfileSerializer,
)
from .serializers import UserDetailSerializer
from ..common import get_object_or_404
from ..posts.models import Post, Attachment


@api_view(["GET"])
def get_user_points(request):
    points = Point.objects.get(user=request.user)
    serializer = PointSerializer(points)
    return Response(serializer.data)


class PostPagination(pagination.PageNumberPagination):
    page_size = 10  # the no. of objects you want to send in one go


class FriendsPostPagination(pagination.PageNumberPagination):
    page_size = 3  # the no. of objects you want to send in one go


class CommentPagination(pagination.PageNumberPagination):
    page_size = 15


@api_view(["GET"])
def get_user_logs(request):
    data = AuditLogs.objects.filter(user=request.user).order_by("-timestamp")[:3]
    serializer = AuditLogSerializer(data, many=True)
    return Response(serializer.data)


class ViewProfile(APIView):
    @staticmethod
    def get(request):
        uid = request.POST.get("uid")
        if not uid:
            message = {"uid": "user uid required"}
            return Response(message, status=HTTP_400_BAD_REQUEST)
        profile = get_object_or_404(
            {"uid": f"user profile with uid: {uid} not found."}, Profile, user_uid=uid
        )
        serializer = UserProfileSerializer(profile)

        return Response(serializer.data, status=HTTP_200_OK)


class EditProfile(APIView):
    @staticmethod
    def post(request):
        _data = request.data.copy()
        user = request.user

        error = {}
        if not _data.get("first_name"):
            error["first_name"] = "first_name is required."
        elif len(_data.get("first_name").strip()) < 3:
            error["first_name"] = "first_name should be at least 3 characters."

        if not _data.get("last_name"):
            error["last_name"] = "last_name is required."
        elif len(_data.get("last_name").strip()) < 3:
            error["last_name"] = "last_name should be at least 3 characters."

        if not _data.get("country"):
            error["country"] = "country is required."

        if not _data.get("city"):
            error["city"] = "city is required."
        elif len(_data.get("city").strip()) < 3:
            error["city"] = "city should be at least 3 characters."

        if len(_data.get("bio")) > 100:
            error["bio"] = "bio should not be long."

        if len(error):
            return Response(error, status=HTTP_400_BAD_REQUEST)

        user.first_name = _data.get("first_name")
        user.last_name = _data.get("last_name")
        user.profile.country = _data.get("country")
        user.profile.city = _data.get("city")
        user.profile.bio = _data.get("bio")
        user.save()
        return Response(data=UserSerializer(user).data, status=HTTP_200_OK)


class FriendsPagination(PageNumberPagination):
    page_size = 8
    page_size_query_param = "page_size"
    max_page_size = 10000


class Friends(generics.ListAPIView):
    serializer_class = FriendsSerializer
    pagination_class = FriendsPagination

    def get_queryset(self):
        return Friend.objects.filter(from_user=self.request.user)


class SuggestedFriends(generics.ListAPIView):
    serializer_class = UserSerializer
    pagination_class = FriendsPagination

    def get_queryset(self):
        from_friends = Friend.objects.filter(from_user=self.request.user).values_list(
            "to_user_id", flat=True
        )
        to_friends = Friend.objects.filter(to_user=self.request.user).values_list(
            "from_user_id", flat=True
        )
        from_friend_requests = FriendRequest.objects.filter(
            from_user=self.request.user
        ).values_list("to_user_id", flat=True)
        to_friend_requests = FriendRequest.objects.filter(
            to_user=self.request.user
        ).values_list("from_user_id", flat=True)

        to_exclude = [
            self.request.user.id,
            *from_friends,
            *to_friends,
            *from_friend_requests,
            *to_friend_requests,
        ]
        return User.objects.filter(
            # Q(profile__city=self.request.user.profile.city)
            # | Q(profile__country=self.request.user.profile.country),
            is_superuser=False,
            is_active=True,
        ).exclude(id__in=to_exclude)


class ReceivedFriendRequests(generics.ListAPIView, generics.CreateAPIView):
    serializer_class = ReceivedFriendRequestSerializer
    pagination_class = FriendsPagination

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, accepted=False)

    def post(self, request, *args, **kwargs):
        _from = get_object_or_404(
            {
                "from_user": f"User with username: {request.data.get('from_user')} not found."
            },
            User,
            username=request.data.get("from_user"),
        )
        _requests = FriendRequest.objects.update_or_create(
            from_user=_from, to_user=request.user, defaults={"accepted": True}
        )
        all_requests_count = FriendRequest.objects.filter(
            to_user=request.user, accepted=False
        ).count()
        unseen_requests = FriendRequest.objects.filter(
            to_user=request.user, accepted=False, seen_at__isnull=True
        )
        unseen_requests_count = unseen_requests.count()
        unseen_requests.update(seen_at=timezone.now())

        async_to_sync(send_friend_request_count)(
            request.user, all_requests_count, unseen_requests_count
        )
        return Response({"success": "Friend request accepted"}, status=HTTP_201_CREATED)


class SentFriendRequests(generics.ListAPIView):
    serializer_class = SentFriendRequestSerializer
    pagination_class = FriendsPagination

    def get_queryset(self):
        return FriendRequest.objects.filter(from_user=self.request.user, accepted=False)


@api_view(["POST"])
def cancel_friend_request(request):
    to_user = request.data.get("to_user")
    FriendRequest.objects.filter(
        from_user=request.user, to_user__username=to_user, accepted=False
    ).delete()
    return Response({"success": "Friend request cancelled"}, status=HTTP_201_CREATED)


@api_view(["POST"])
def cancel_incoming_friend_request(request):
    from_user = request.data.get("from_user")
    FriendRequest.objects.filter(
        from_user__username=from_user, to_user=request.user, accepted=False
    ).delete()
    all_requests_count = FriendRequest.objects.filter(
        to_user=request.user, accepted=False
    ).count()
    unseen_requests_count = FriendRequest.objects.filter(
        to_user=request.user, accepted=False, seen_at__isnull=True
    ).count()
    async_to_sync(send_friend_request_count)(
        request.user, all_requests_count, unseen_requests_count
    )

    return Response({"success": "Friend request cancelled"}, status=HTTP_201_CREATED)


class SendFriendRequest(APIView):
    @staticmethod
    def post(request):
        _from = request.user
        _to: User = get_object_or_404(
            {
                "to_user": f"User with username: {request.data.get('to_user')} not found."
            },
            User,
            username=request.data.get("to_user"),
        )

        _blocked_users, _ = BlockedUser.objects.get_or_create(user=_from)
        if _blocked_users.blocked_users.filter(uid=_to.uid).exists():
            return Response(
                {"error": f"Unblock {_to.username} to add as a friend"},
                status=HTTP_401_UNAUTHORIZED,
            )

        _request = FriendRequest.objects.create(from_user=_from, to_user=_to)
        _all_request_count: int = FriendRequest.objects.filter(
            to_user=_to, accepted=False
        ).count()
        _unseen_request_count: int = FriendRequest.objects.filter(
            to_user=_to, accepted=False, seen_at__isnull=True
        ).count()
        async_to_sync(send_friend_request_count)(
            _to, _all_request_count, _unseen_request_count
        )
        async_to_sync(send_friend_request)(
            _to, f"you have a friend request from {_from.username}"
        )

        return Response(
            {"success": f"friend request sent to {_to.username}"},
            status=HTTP_201_CREATED,
        )


@api_view(["GET"])
def get_user_details(request, username):
    user = get_object_or_404(
        {"username": f"User with username: {username} not found."},
        User,
        username=username,
    )

    serializer = UserDetailSerializer(user, context={"user": request.user})
    return Response(serializer.data, status=HTTP_200_OK)


@transaction.atomic()
@api_view(["POST"])
def unfriend(request):
    user = get_object_or_404(
        {"username": f"User with uid: {request.data.get('uid')} not found."},
        User,
        uid=request.data.get("uid"),
    )

    Friend.objects.filter(
        Q(from_user=user, to_user=request.user)
        | Q(from_user=request.user, to_user=user)
    ).delete()

    return Response(
        {"success": f"you have un-friend-ed {user.username}"}, status=HTTP_200_OK
    )


@api_view(["POST"])
def change_avatar(request):
    new_pic = request.data.get("avatar")
    if not new_pic:
        return Response({"error": "Avatar is required."}, status=HTTP_400_BAD_REQUEST)

    _data = request.data.copy()
    profile = Profile.objects.get(user=request.user)
    serializer = AvatarImageSerializer(profile, data=_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"success": "profile picture change successfully."}, status=HTTP_201_CREATED
        )
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def change_cover(request):
    new_pic = request.data.get("coverpic")
    if not new_pic:
        return Response(
            {"error": "cover pic is required."}, status=HTTP_400_BAD_REQUEST
        )

    _data = request.data.copy()
    profile = Profile.objects.get(user=request.user)
    serializer = CoverImageSerializer(profile, data=_data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {"success": "cover picture change successfully."}, status=HTTP_201_CREATED
        )
    return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


# block user
@api_view(["POST"])
def block_user(request):
    user = get_object_or_404(
        {"uid": f"User with uid: {request.data.get('uid')} not found."},
        User,
        uid=request.data.get("uid"),
    )

    obj, _ = BlockedUser.objects.get_or_create(user=request.user)

    if obj.blocked_users.filter(uid=user.uid).exists():
        obj.blocked_users.remove(user)
        message = f"You have unblocked {user.username}."
        return Response({"success": message}, status=HTTP_201_CREATED)
    else:
        obj.blocked_users.add(user)
        obj.save()
        message = f"You have blocked {user.username}."
        return Response({"success": message}, status=HTTP_201_CREATED)


@api_view(["POST"])
def request_celeb_verify(request):
    category = request.data.get("category", None)
    if category and category in ("pg", "cb"):
        created = CelebVerification.objects.create(
            user=request.user, category=category, status=CelebVerification.REQUESTED
        )

        if created:
            return Response(
                {"success": "Successfully Requested"}, status=HTTP_201_CREATED
            )
    else:
        return Response(
            {
                "error": "Category must not be empty and be either 'pg':Page or 'cb': Celebrity, "
                "others are not accepted",
            },
            status=HTTP_400_BAD_REQUEST,
        )
    return Response({"message": "Could not be Requested"}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def respond_celeb_verify_request(request, celeb_verify_id):
    status = request.data.get("status", None)
    if status == "accept":
        response = CelebVerification.ACCEPTED
    elif status == "decline":
        response = CelebVerification.DECLINED
    else:
        return Response(
            {"error": "status value required. 'accept' or 'decline' only accepted"},
            status=HTTP_400_BAD_REQUEST,
        )
    CelebVerification.objects.filter(id=celeb_verify_id).update(status=response)

    return Response({"success": f"Request {status}d"}, status=HTTP_200_OK)


@api_view(["GET"])
def user_posts_gallery(request, username):
    gallery_list = (
        Post.objects.filter(
            user__username__iexact=username,
            attachments__isnull=False,
            attachments__category__in=[Attachment.IMAGE, Attachment.VIDEO],
        )
        .annotate(
            attachment_public_url=Concat(Value(settings.MEDIA_URL), "attachments__url")
        )
        .values_list("attachment_public_url", flat=True)
    )

    return Response({"gallery": list(gallery_list)}, status=HTTP_200_OK)
