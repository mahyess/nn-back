from rest_framework import serializers
from .models import Badge, Point


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'icon', 'name', 'timestamp']


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['total_points', 'color_code']
