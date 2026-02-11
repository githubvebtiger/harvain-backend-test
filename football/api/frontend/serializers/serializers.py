from rest_framework import serializers as rest_serializers

from bets.api.frontend import serializers as bets_serializers

# region				-----External Imports-----
from geo.api.general import serializers as geo_serializers

# region				-----Internal Imports-----
from ...general import serializers as general_serializers

# endregion

# endregion


class ReadMatchSerializer(general_serializers.MatchBaseSerializer):
    home_team = general_serializers.TeamBaseSerializer(many=False)
    away_team = general_serializers.TeamBaseSerializer(many=False)
    winer = general_serializers.TeamBaseSerializer(many=False)
    odds = bets_serializers.ReadOddsSerializer(many=True)

    # region                -----Metadata-----
    class Meta(general_serializers.MatchBaseSerializer.Meta):
        fields = general_serializers.MatchBaseSerializer.Meta.fields + [
            "home_team",
            "away_team",
            "winer",
            "date",
            "referee",
            "odds",
        ]

    # endregion


class ReadMatchLeagueSerializer(ReadMatchSerializer):
    main_odds_1 = rest_serializers.DecimalField(decimal_places=2, max_digits=100)
    main_odds_x = rest_serializers.DecimalField(decimal_places=2, max_digits=100)
    main_odds_2 = rest_serializers.DecimalField(decimal_places=2, max_digits=100)

    # region                -----Metadata-----
    class Meta(ReadMatchSerializer.Meta):
        fields = ReadMatchSerializer.Meta.fields + [
            "main_odds_1",
            "main_odds_x",
            "main_odds_2",
        ]

    # endregion


class ReadLeagueSerializer(general_serializers.LeagueBaseSerializer):
    matches = ReadMatchLeagueSerializer(many=True)
    country = geo_serializers.CountryBaseSerializer(many=False)

    # region                -----Metadata-----
    class Meta(general_serializers.LeagueBaseSerializer.Meta):
        fields = general_serializers.LeagueBaseSerializer.Meta.fields + [
            "title",
            "logo",
            "flag",
            "season",
            "round",
            "country",
            "matches",
        ]

    # endregion
