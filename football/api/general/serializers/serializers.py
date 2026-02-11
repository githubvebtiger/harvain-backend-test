# region				-----External Imports-----
from rest_framework import serializers as rest_serializers

# region				-----Internal Imports-----
from .... import models as football_models

# endregion

# endregion


class TeamBaseSerializer(rest_serializers.ModelSerializer):
    # region                -----Metadata-----
    class Meta(object):
        fields = ["id", "title", "logo"]
        model = football_models.Team

    # endregion


class MatchBaseSerializer(rest_serializers.ModelSerializer):
    # region                -----Metadata-----
    class Meta(object):
        fields = ["id"]
        model = football_models.Match

    # endregion


class LeagueBaseSerializer(rest_serializers.ModelSerializer):
    # region                -----Metadata-----
    class Meta(object):
        fields = ["id", "kind_of_sport"]
        model = football_models.League

    # endregion
