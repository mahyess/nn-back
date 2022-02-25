from collections import OrderedDict

# from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework import pagination, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param, remove_query_param
from rest_framework.views import APIView

from namastenepal.community.models import Community
from namastenepal.community.serializers import CommunitySearchSerializer
from namastenepal.core.models import PrivacyPolicy, Term, StoragePolicy, User
from namastenepal.posts.models import Post
from namastenepal.posts.serializers import PostSearchSerializer
from namastenepal.posts.sorting import hot_sort
from namastenepal.usermodule.models import BlockedUser, Friend
from namastenepal.usermodule.serializers import UserCardSerializer


def privacy_policy(request):
    content = PrivacyPolicy.objects.all()
    ctx = {"data": content}

    return render(request, "legal/privacy.html", ctx)


def storage_tech(request):
    content = StoragePolicy.objects.all()
    ctx = {"data": content}

    return render(request, "legal/storage.html", ctx)


def terms(request):
    content = Term.objects.all()
    ctx = {"data": content}

    return render(request, "legal/terms.html", ctx)


class SearchPagination(pagination.PageNumberPagination):
    page_size = 5  # the no. of objects you want to send in one go

    # this source here acts as single parameter for pagination
    # takes either "posts" "users" "samajs"
    def get_paginated_response(self, data, source=None):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link(source)),
                    ("previous", self.get_previous_link(source)),
                    ("results", data),
                ]
            )
        )

    def get_next_link(self, source=None):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        # add param to url like {{url}}/?source=1
        url = replace_query_param(url, source, "1")
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self, source=None):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        url = replace_query_param(url, source, "1")
        return replace_query_param(url, self.page_query_param, page_number)


class SearchAPI(APIView):
    _paginator: SearchPagination

    def get_posts_queryset(self, q):
        if self.request.user.is_authenticated:
            to_filter = Community.objects.filter(
                Q(subscriber_gender_id=self.request.user.gender.id)
                | Q(subscriber_gender__isnull=True),
                is_private=False,
            )
        else:
            to_filter = Community.objects.filter(
                subscriber_gender__isnull=True, is_private=False
            )

        return hot_sort(
            Post.objects.filter(
                # Q(community__isnull=True)|
                Q(community__in=to_filter),
                Q(title__icontains=q) | Q(body__icontains=q),
                pinned=False,
                # timestamp__gte=end_date
            )
        )

    def get_users_queryset(self, q):
        user = self.request.user

        try:
            blocked_users = list(
                BlockedUser.objects.get(user=user).blocked_users.values_list(
                    "id", flat=True
                )
            )
        except BlockedUser.DoesNotExist:
            blocked_users = []

        try:
            blocked_by_users = list(
                user.blocked_by_users.all().values_list("id", flat=True)
            )
        except BlockedUser.DoesNotExist:
            blocked_by_users = []

        to_exclude = [user.id, *blocked_users, *blocked_by_users]

        return (
            User.objects.filter(
                Q(full_name__icontains=q) | Q(username__icontains=q) | Q(email=q),
                is_superuser=False,
            )
            .exclude(id__in=to_exclude)
            .order_by("username")
        )

    def get_friends_queryset(self, q):
        user: User = self.request.user

        return User.objects.filter(
            Q(full_name__icontains=q) | Q(username__icontains=q) | Q(email=q),
            from_user__in=Friend.objects.filter(from_user=user),  # friend from
            is_superuser=False,
        ).order_by("username")

    def get_samajs_queryset(self, q):
        return Community.objects.filter(
            Q(subscriber_gender=self.request.user.gender)
            | Q(subscriber_gender__isnull=True),
            Q(name__icontains=q) | Q(description__icontains=q),
            is_private=False,
        ).order_by("id")

    permission_classes = ()
    # serializer_class = PostSearchSerializer
    pagination_class = SearchPagination

    def get(self, request, **kwargs):
        q = self.request.GET.get("q", "")
        search_posts = self.request.GET.get("posts", None)
        search_users = self.request.GET.get("users", None)
        search_friends = self.request.GET.get("friends", None)
        search_samajs = self.request.GET.get("samajs", None)

        # if none are provided, search all of them
        search_all = not (
            search_posts or search_users or search_samajs or search_friends
        )

        res = {"q": q}

        if search_posts or search_all:
            page = self.paginate_queryset(self.get_posts_queryset(q))
            if page is not None:
                serializer = PostSearchSerializer(page, many=True)

                # this second param for paginated response is used for
                # generating next and previous links for the particular category only
                res["posts"] = self.get_paginated_response(
                    serializer.data, "posts"
                ).data

        if search_users or search_all:
            page = self.paginate_queryset(self.get_users_queryset(q))
            if page is not None:
                serializer = UserCardSerializer(page, many=True)
                res["users"] = self.get_paginated_response(
                    serializer.data, "users"
                ).data

        if search_friends:
            page = self.paginate_queryset(self.get_friends_queryset(q))
            if page is not None:
                serializer = UserCardSerializer(page, many=True)
                res["friends"] = self.get_paginated_response(
                    serializer.data, "friends"
                ).data

        if search_samajs or search_all:
            page = self.paginate_queryset(self.get_samajs_queryset(q))
            if page is not None:
                serializer = CommunitySearchSerializer(page, many=True)
                res["samajs"] = self.get_paginated_response(
                    serializer.data, "samajs"
                ).data

        return JsonResponse(res)

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

    def get_paginated_response(self, data, source):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data, source)
