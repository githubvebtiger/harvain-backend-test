# region				-----External Imports-----
from rest_framework import serializers as rest_serializers

# region				-----Internal Imports-----
from .... import models as geo_models

# endregion

# endregion


class CountryBaseSerializer(rest_serializers.ModelSerializer):
    # region                -----Metadata-----
    class Meta(object):
        fields = ["id", "title"]
        model = geo_models.Country

    # endregion
