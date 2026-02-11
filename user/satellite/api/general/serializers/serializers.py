# region				-----External Imports-----
from rest_framework import serializers as rest_serializers

# region				-----Internal Imports-----
from .... import models as satellite_models

# endregion

# endregion


class SatelliteBaseSerializer(rest_serializers.ModelSerializer):
    # region                -----Metadata-----
    class Meta(object):
        fields = ["id", "uuid", "username"]
        model = satellite_models.Satellite

    # endregion
