from rest_framework import serializers as rest_serializers

from ....models import News


class ReadNewsSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ["image", "header", "content", "link"]
