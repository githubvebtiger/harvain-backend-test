# region				-----External Imports-----
from rest_framework import serializers as rest_serializers

# region				-----Internal Imports-----
from .... import models as bets_models

# endregion

# endregion


class OddsBaseSerializer(rest_serializers.ModelSerializer):
    # region                -----Metadata-----
    class Meta(object):
        fields = ["id"]
        model = bets_models.Odds

    # endregion


class BetBaseSerializer(rest_serializers.ModelSerializer):
    # region                -----Metadata-----
    class Meta(object):
        fields = ["id"]
        model = bets_models.Bet

    # endregion


class OddsDetailBaseSerializer(rest_serializers.ModelSerializer):
    # region                -----Metadata-----
    class Meta(object):
        fields = ["id", "name"]
        model = bets_models.OddsDetail

    # endregion
