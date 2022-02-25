# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.contrib.auth import get_user_model
from rest_framework import serializers
from friendship.models import FriendshipRequest
from namastenepal.accounts.serializers import UserProfileSerializer


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = get_user_model()
        fields = ('pk', 'username', 'email', 'profile')


class FriendshipRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer()

    class Meta:
        model = FriendshipRequest
        fields = ('id', 'from_user', 'message', 'created')
