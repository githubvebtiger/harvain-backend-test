from rest_framework import serializers as rest_serializers

from .... import models as user_models


class ClientBaseSerializer(rest_serializers.ModelSerializer):
    # region                -----Metadata-----
    class Meta(object):
        fields = ["id", "username"]
        model = user_models.Client

    # endregion
