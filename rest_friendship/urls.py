# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from .views import FriendViewSet, FriendshipRequestViewSet, ViewFriendRequests

from rest_framework.routers import DefaultRouter
from django.urls import path

router = DefaultRouter()
router.register(r'friends', FriendViewSet, base_name='friends')
router.register(r'friendrequests', FriendshipRequestViewSet, base_name='friendrequests')
urlpatterns = [

    path('requests/',ViewFriendRequests.as_view())

]+router.urls
