from rest_framework import serializers as rest_serializers

from .... import models as user_models


class UserBaseSerializer(rest_serializers.ModelSerializer):
    # region                -----Metadata-----
    class Meta(object):
        fields = ["id", "username"]
        model = user_models.Satellite

    # endregion


class RequisitesBaseSerializer(rest_serializers.ModelSerializer):
    # region                -----Metadata-----
    class Meta(object):
        fields = ["id", "title"]
        model = user_models.Requisites

    # endregion
