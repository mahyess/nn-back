from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from graphene_django.views import GraphQLView
from rest_framework import serializers
from rest_framework.decorators import (
    authentication_classes,
    permission_classes,
    api_view,
)
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request as DRFRequest
from rest_framework.settings import api_settings

from namastenepal.core.models import HashTag


class PrivateGraphQLView(GraphQLView):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PrivateGraphQLView, self).dispatch(request, *args, **kwargs)

    def parse_body(self, request):
        if isinstance(request, DRFRequest):
            return request.data
        return super(PrivateGraphQLView, self).parse_body(request)

    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(PrivateGraphQLView, cls).as_view(*args, **kwargs)
        view = permission_classes((IsAuthenticated,))(view)
        view = authentication_classes(api_settings.DEFAULT_AUTHENTICATION_CLASSES)(view)
        view = api_view(["GET", "POST"])(view)
        return view


class HashTagListSerializer(serializers.ModelSerializer):
    total_posts_count = serializers.SerializerMethodField()

    @staticmethod
    def get_total_posts_count(obj):
        return obj.hash_tag_posts.count()

    total_posts_count_72_hours = serializers.SerializerMethodField()

    @staticmethod
    def get_total_posts_count_72_hours(obj):
        return obj.hash_tag_posts.filter(
            timestamp__gte=timezone.now() - timedelta(days=3)
        ).count()

    total_posts_count_24_hours = serializers.SerializerMethodField()

    @staticmethod
    def get_total_posts_count_24_hours(obj):
        return obj.hash_tag_posts.filter(
            timestamp__gte=timezone.now() - timedelta(days=1)
        ).count()

    class Meta:
        model = HashTag
        fields = "__all__"


class HashTagList(ListAPIView):
    serializer_class = HashTagListSerializer
    queryset = HashTag.objects.annotate(
        number_of_posts=Count(
            "hash_tag_posts__id",
            filter=Q(hash_tag_posts__timestamp__gte=timezone.now() - timedelta(days=1)),
            distinct=True,
        )
    ).order_by("-number_of_posts")[:10]


class FrontendAppView(View):
    """
    Serves the compiled frontend entry point (only works if you have run `yarn
    run build`).
    """

    @staticmethod
    def get(request):
        try:
            return render(request, "build/index.html")
        except FileNotFoundError:
            return HttpResponse(
                """
                This URL is only used when you have built the production
                version of the app. Visit http://localhost:3000/ instead, or
                run `yarn run build` to test the production version.
                """,
                status=501,
            )
