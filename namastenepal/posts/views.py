import re

from asgiref.sync import async_to_sync
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.http import JsonResponse
from rest_framework import pagination
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_201_CREATED,
    HTTP_200_OK,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.views import APIView

from namastenepal.channels_app.signals import (
    send_notification,
    send_unread_notification,
    send_fcm_push_notification,
)
from namastenepal.community.models import Community
from namastenepal.community.utils import start_new_thread, compressImage
from namastenepal.core.models import HashTag, User
from namastenepal.points.pointSystem import PointSystem
from namastenepal.usermodule.models import Friend, BlockedUser
from .models import Post, Comment, Attachment
from .serializers import (
    PostSerializer,
    CommentSerializer,
    CreatePostSerializer,
)
from .sorting import hot_sort, trend_sort
from ..common import get_object_or_404
from ..notifications.models import Notification
from ..notifications.views import create_notification


class PostPagination(pagination.PageNumberPagination):
    page_size = 5  # the no. of objects you want to send in one go


def communities_to_filter():
    pass


class PostAPI(APIView):
    _paginator: PostPagination

    def get_queryset(self):
        # start_date = datetime.datetime.now()
        # end_date = start_date + datetime.timedelta(days=-3)
        # end_date = make_aware(end_date)
        q = self.request.GET.get("q", "")
        queryset = Post.objects.filter()

        if (
                self.request.user.is_authenticated
                and self.request.GET.get("source") == "subscribed"
        ):
            to_filter = Community.objects.filter(
                Q(subscriber_gender_id=self.request.user.gender.id)
                | Q(subscriber_gender__isnull=True),
                is_private=False,
            )
        else:
            to_filter = Community.objects.filter(
                subscriber_gender__isnull=True, is_private=False
            )

        _order_by = self.request.GET.get("order_by", "hot")

        if _order_by not in ["hot", "new", "trending"]:
            _order_by = "hot"

        if _order_by == "new":
            queryset = queryset.filter(
                # Q(community__isnull=True)|
                # shows both user and samaj posts, here no user profile posts
                Q(community__in=to_filter),
                Q(title__icontains=q) | Q(body__icontains=q),
                pinned=False,
                # timestamp__gte=end_date
            ).order_by("-timestamp")
        elif _order_by == "hot":
            queryset = hot_sort(
                queryset.filter(
                    # Q(community__isnull=True)|
                    Q(community__in=to_filter),
                    Q(title__icontains=q) | Q(body__icontains=q),
                    pinned=False,
                    # timestamp__gte=end_date
                )
            )
        elif _order_by == "trending":
            queryset = hot_sort(
                queryset.filter(
                    # Q(community__isnull=False),
                    Q(hash_tags__isnull=False),
                    # Q(community__in=to_filter),
                    Q(title__icontains=q) | Q(body__icontains=q),
                    pinned=False,
                    # timestamp__gte=end_date
                )
            )

        return queryset

    permission_classes = ()
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)
    serializer_class = PostSerializer
    pagination_class = PostPagination

    def get(self, request, **kwargs):
        queryset = self.get_queryset()
        if hasattr(queryset, "status_code"):
            return queryset

        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            return self.get_paginated_response(serializer.data)

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    @staticmethod
    def post(request, *args, **kwargs):
        _data = request.data.copy()
        print(_data)
        user = request.user
        cid = _data.get("community_id", None)

        _cmm = None
        if cid:
            _cmm = get_object_or_404(
                {"community_id": f"community with id: {cid} not found"},
                Community,
                id=cid,
            )

        title = _data.get("title", None)
        if title is None and _cmm:
            return Response(data={"title": "Title is required"}, status=400)
        body = _data.get("body", None)
        shared_post_id = _data.get("shared_post_id", None)
        if shared_post_id:
            _data["shared_post"] = get_object_or_404(
                {"shared_post_id": f"post with id: {shared_post_id} not found"},
                Post,
                pid=shared_post_id,
            ).id
        else:
            if body is None:
                return Response(
                    data={"body": "Post Content is required in an Original Post"},
                    status=400,
                )
        attachments = dict(_data.lists()).get("attachments", None)
        # unusable because of unknown reasons
        # images = _data.get('images', None)

        _data["user"] = user.id
        _data["community"] = _cmm.id if _cmm else None

        serializer = CreatePostSerializer(data=_data)
        if serializer.is_valid():
            serializer.save()
            message = {"success": "Post created successfully."}
            created_post = Post.objects.get(pid=serializer.data["pid"])

            if attachments:
                for attachment in attachments:
                    if attachment is None or str(attachment).strip() in [
                        "",
                        "null",
                        "None",
                        "none",
                        "Null",
                    ]:
                        continue
                    content_type = attachment.content_type
                    attachment_instance = Attachment()
                    attachment_instance.url = attachment
                    if "image" in content_type:
                        attachment_instance.category = Attachment.IMAGE
                    elif "video" in content_type:
                        attachment_instance.category = Attachment.VIDEO
                    elif any(
                            x in content_type for x in ["application/pdf", "text/plain"]
                    ):
                        attachment_instance.category = Attachment.DOCUMENT
                    else:
                        raise ValidationError(
                            detail={
                                "attachment": f"content type: {content_type} is not supported"
                            },
                            code=HTTP_400_BAD_REQUEST,
                        )
                    attachment_instance.save()
                    created_post.attachments.add(attachment_instance)
                created_post.save()

            return Response(
                {**message, "post": PostSerializer(created_post).data},
                status=HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class CommunityPostAPI(PostAPI):
    def get_queryset(self):
        _order_by = self.request.GET.get("order_by", "hot")
        if _order_by not in ["hot", "new"]:
            _order_by = "hot"

        community = Community.objects.get(
            id=self.kwargs.get("id"), slug=self.kwargs.get("slug")
        )
        queryset = Post.objects.filter()

        if _order_by == "new":
            queryset = queryset.filter(community=community, pinned=False).order_by(
                "-timestamp"
            )
        elif _order_by == "hot":
            queryset = hot_sort(queryset.filter(community=community, pinned=False))

        return queryset


class HashTagPostAPI(PostAPI):
    def get_queryset(self):
        # _order_by = self.request.GET.get('order_by', 'hot')
        # if _order_by not in ['hot', 'new']:
        #     _order_by = "hot"

        hash_tag = HashTag.objects.get(title=self.kwargs.get("hashtag"))

        return trend_sort(hash_tag.hash_tag_posts.filter(community__isnull=True))

        # if _order_by == "new":
        #     queryset = Post.objects.filter(
        #         community=community, pinned=False).order_by("-timestamp")
        # elif _order_by == "hot":
        # queryset = hot_sort(Post.objects.filter(
        #     community=community, pinned=False))

        # return queryset


class PostDetailAPI(APIView):
    permission_classes = ()

    @staticmethod
    def get(
            request, slug_or_id
    ):  # to query for post with either id of the post or slug
        try:
            filter_arg = Q(slug=slug_or_id)  # if query matches with slug
            try:
                filter_arg |= Q(id=int(slug_or_id))  # if query matched with id
            except ValueError:
                # try catch block to bypass
                # "invalid literal for int() with base 10:" error
                pass
            post = Post.objects.get(filter_arg)
            serializer = PostSerializer(post)

            if request.user.is_authenticated:
                Notification.objects.filter(
                    user=request.user, post_notification__post=post, seen=False
                ).filter(seen=True)
                total_unread = Notification.objects.filter(
                    user=request.user, seen=False
                ).count()

                async_to_sync(send_unread_notification)(
                    request.user.username, total_unread
                )

            return Response(serializer.data)
        except Exception as e:
            print(e)
            ctx = {"error": "Post not found."}
            return JsonResponse(ctx, status=HTTP_404_NOT_FOUND)


@api_view(["POST"])
def like(request, pid):
    try:
        user: User = request.user
        post = Post.objects.get(deleted__isnull=True, pid=pid)

        if post.likes.filter(uid=user.uid).exists():
            post.likes.remove(user)
            message = "removed namaste from the post."
        else:
            post.likes.add(user)
            message = "added namaste on the post."

        ctx = {"likes_count": post.total_likes, "message": message}
        return Response(ctx, status=HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({"error": "error"}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def delete(request):
    pid = request.data.get("pid")
    post = get_object_or_404({"pid": f"post with id: {pid} not found."}, Post, pid=pid)

    if post.user == request.user:
        post.delete()
        return Response({"success": "Post deleted successfully"}, status=HTTP_200_OK)
    else:
        return Response(
            {"error": "You are not authorized."}, status=HTTP_401_UNAUTHORIZED
        )


class Comments(APIView):
    _paginator: PostPagination
    permission_classes = ()
    serializer_class = CommentSerializer
    pagination_class = PostPagination

    def get_queryset(self):
        order = self.request.GET.get("order_by", None)
        if order not in ["top", "timestamp"]:
            order = "top"

        # post = Post.objects.get(deleted__isnull=True, pid=self.kwargs['pid'])
        return (
            Comment.objects.filter(post__pid=self.kwargs["pid"], parent__isnull=True)
                .annotate(top=Count("up_votes"))
                .order_by("-" + str(order))
        )

    def get(self, request, *args, **kwargs):
        if not self.get_queryset() is None:
            page = self.paginate_queryset(self.get_queryset())
            if page is not None:
                serializer = self.serializer_class(
                    page, many=True, context={"request": self.request}
                )
                return self.get_paginated_response(serializer.data)
        else:
            data = {"error": "Error on fetching comments."}
            return Response(data, status=HTTP_400_BAD_REQUEST)

    @property
    def paginator(self):
        if not hasattr(self, "_paginator"):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

    def post(self, request, pid):
        comment = request.data.get("comment", "")
        if len(comment.strip()) == 0:
            return Response(
                {"comment": "Comment content required"}, status=HTTP_400_BAD_REQUEST
            )

        user: User = request.user

        try:
            _post = Post.objects.get(deleted__isnull=True, pid=pid)
            parent_comment_id = request.data.get("parent", None)
            parent = None  # just to silence warning!!!
            # print(parent_comment_id)
            comment_types = {
                "comment": "comment",
                "reply": "reply",
                "request": "request",
            }
            if parent_comment_id:
                parent = Comment.objects.get(id=parent_comment_id)
                if user in parent.discuss_group.all():
                    task = Comment.objects.create(
                        user=user,
                        post=_post,
                        comment=comment,
                        parent=parent,
                        approved=True,
                    )
                    message = " replied on a chalfal on the post."
                    comment_type = comment_types.get("reply")
                else:
                    return Response(
                        {"comment": "You cant reply to this comment"},
                        status=HTTP_400_BAD_REQUEST,
                    )
                    # ''' this to be uncommented if reply approval system is implemented '''
                    # task = Comment.objects.create(user=user, post=_post, comment=comment, parent=parent)
                    # message = " requested to add a chalfal on the post."
                    # comment_type = comment_types.get('request')
            else:
                task = Comment.objects.create(user=user, post=_post, comment=comment)
                message = " added a chalfal on the post."
                comment_type = comment_types.get("comment")

            task.save()
            serializer = CommentSerializer(task, context={"request": self.request})

            ctx = {"message": message, "comment": serializer.data}

            return Response(ctx, status=HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({"comment": "Invalid request"}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def approve_reply(request):
    comment = request.data.get("comment")
    _comment = get_object_or_404(
        {"comment": f"comment with id: {comment} not found."}, Comment, id=comment
    )

    if request.user in _comment.parent.discuss_group.all():
        _comment.approved = True
        _comment.save()
        return Response({"comment": "reply approved"}, status=HTTP_200_OK)
    else:
        return Response({"error": "not authorized"}, status=HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
def reject_reply(request):
    comment_id = request.data.get("comment")
    comment = get_object_or_404(
        {"comment": f"comment with id: {comment_id} not found."}, Comment, id=comment_id
    )
    if comment.approved is not None:
        return Response(
            {"error": "comment already responded. cannot reject"},
            status=HTTP_400_BAD_REQUEST,
        )

    if request.user in comment.parent.discuss_group.all():
        comment.approved = False
        comment.save()
        return Response({"comment": "reply rejected"}, status=HTTP_200_OK)
    else:
        return Response({"error": "not authorized"}, status=HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
def remove_from_discussion(request):
    parent_comment_id = request.data.get("parent_comment")
    removable_user_id = request.data.get("removable_user_id")
    comments_deletable = request.data.get("delete_comments", False)

    parent_comment = get_object_or_404(
        {"comment": f"comment with id: {parent_comment_id} not found."},
        Comment,
        id=parent_comment_id,
    )
    if request.user is parent_comment.user or request.user is parent_comment.post.user:

        removable_user_id = get_user_model().objects.get(id=removable_user_id)
        if removable_user_id in parent_comment.discuss_group.all():
            parent_comment.discuss_group.remove(removable_user_id)
            if comments_deletable:
                for deletable_comment in Comment.objects.filter(
                        user=removable_user_id, parent=parent_comment
                ):
                    deletable_comment.approved = False
                    deletable_comment.save()
            return Response(
                {"comment": "user removed from discussion group"}, status=HTTP_200_OK
            )
        else:
            return Response(
                {"error": "user not found in discussion group"},
                status=HTTP_400_BAD_REQUEST,
            )
    else:
        return Response({"error": "not authorized"}, status=HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
def up_vote(request):
    comment_id = request.data.get("comment")
    user: User = request.user

    comment: Comment = get_object_or_404(
        {"comment": f"comment with id: {comment_id} not found."}, Comment, id=comment_id
    )

    if not comment.up_votes.filter(uid=user.uid).exists():
        if comment.down_votes.filter(uid=user.uid).exists():
            comment.down_votes.remove(user)
        comment.up_votes.add(user)

        message = "up voted."
    else:
        message = "already up voted."

    return Response(
        {
            "message": message,
            "total_votes_count": comment.total_votes,
            "comment_id": comment.id,
        },
        status=HTTP_200_OK,
    )


@api_view(["POST"])
def down_vote(request):
    comment_id = request.data.get("comment")
    user: User = request.user

    comment: Comment = get_object_or_404(
        {"comment": f"comment with id: {comment_id} not found."}, Comment, id=comment_id
    )

    ps = PointSystem()
    if not comment.down_votes.filter(uid=user.uid).exists():
        if not comment.up_votes.filter(uid=user.uid).exists():
            comment.down_votes.add(user)
        comment.up_votes.remove(user)
        comment.down_votes.add(user)

        message = "down voted."
        # add point
        if comment.post.community:
            _ = ps.manage_points(_type="vote_down", comment=comment)
    else:
        message = "already down voted."

    return Response(
        {
            "message": message,
            "total_votes_count": comment.total_votes,
            "comment_id": comment.id,
        },
        status=HTTP_200_OK,
    )


def modify_input_for_multiple_files(image):
    return {"url": image}


class Report(APIView):
    @staticmethod
    def post(request):
        user = request.user

        pid = request.data.get("pid", None)
        post = get_object_or_404(
            {"pid": f"post with id: {pid} not found."}, Post, pid=pid
        )

        if post.reports.filter(uid=user.uid).exists():
            message = "you have already reported."
        else:
            community = Community.objects.get(id=post.community.id)
            if user in community.subscribers.all():
                post.reports.add(user)
                message = "post reported."
                delete_report_exceeded(post)
            else:
                message = f"join {community.name} to report."

        return Response({"message": message}, status=HTTP_200_OK)


def data_to_json(notification):
    return {
        "id": str(notification.id),
        "action": notification.action,
        "from_user": str(notification.from_user),
        "user": str(notification.user),
        "post": str(notification.post.slug),
        "seen": str(notification.seen),
        "timestamp": str(notification.timestamp),
    }


def delete_report_exceeded(post):
    _id = post.community.id
    community = Community.objects.get(id=_id)
    total_subscribers = community.subscribers.all().count()
    avg = 51 / 100 * float(total_subscribers)
    number_of_reports = post.reports.all().count()
    if float(number_of_reports) >= avg:
        message = "post deleted due to maximum reports."
        task = Notification.objects.create(
            user=post.user,
            from_user=post.user,
            action=message,
            post_notification__post=post,
        )
        task.save()
        async_to_sync(send_notification)(
            username=str(post.user.username), data=data_to_json(task)
        )
        ps = PointSystem()
        # status = ps.manage_points(user=post.user, _type="reportedPost")
        _ = ps.manage_points(_type="reported_post")
        post.delete()
        return Response({"message": message}, status=HTTP_200_OK)


class UserPosts(PostAPI):
    http_method_names = ["get"]

    def get_queryset(self):
        source = self.request.GET.get("source", "both")
        if source not in ["profile", "samaj", "tagged", "both"]:
            source = "both"
        try:
            username = self.kwargs.get("username")
            if username == self.request.user.username:
                user = self.request.user
            else:
                user = get_user_model().objects.get(username=username)
                _blocked_users, _ = BlockedUser.objects.get_or_create(
                    user=self.request.user
                )
                if _blocked_users.blocked_users.filter(username=user.username).exists():
                    return Response({
                        "info": "You have blocked {}. Unblock to view personal posts.".format(
                            user.username
                        )},
                        status=HTTP_401_UNAUTHORIZED,
                    )

                if not Friend.objects.filter(
                        Q(from_user=self.request.user, to_user=user)
                        | Q(from_user=user, to_user=self.request.user)
                ).exists():
                    return Response({
                        "info": f"Add {user.username} as a friend to view personal posts."
                    }, status=HTTP_401_UNAUTHORIZED,
                    )

            if source == "profile":
                return Post.objects.filter(user=user, community__isnull=True).order_by(
                    "-timestamp"
                )
            if source == "tagged":
                return Post.objects.filter(tags__in=[user]).order_by("-timestamp")
            elif source == "samaj":
                return Post.objects.filter(user=user, community__isnull=False).order_by(
                    "-timestamp"
                )
            elif source == "both":
                return Post.objects.filter(user=user).order_by("-timestamp")

        except get_user_model().DoesNotExist:
            return Response({"error": "no user found"}, status=HTTP_404_NOT_FOUND)

        # return Post.objects.filter(user=request.user)


class FriendsPosts(PostAPI):
    def get_queryset(self):
        friends = Friend.objects.filter(from_user=self.request.user)
        posts = Post.objects.filter(
            community__isnull=True, user__in=[x.to_user for x in friends]
        ).order_by("-timestamp")
        return posts


@api_view(["GET"])
def get_pinned_post(request, samaj):
    community = get_object_or_404(
        {"samaj": f"samaj with id: {samaj} not found."}, Community, id=samaj
    )

    posts = Post.objects.filter(community=community, pinned=True).last()
    if posts is None:
        return Response({}, status=HTTP_200_OK)

    serializer = PostSerializer(posts)
    return Response(serializer.data, status=HTTP_200_OK)
