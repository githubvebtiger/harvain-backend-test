# region				-----External Imports-----
from datetime import datetime

from rest_framework import serializers as rest_serializers

from ....models import Trade

# region				-----Internal Imports-----
from ...general import serializers as general_serializers

# endregion

# endregion


class ReadOddsAmountSerializer(rest_serializers.Serializer):
    types = rest_serializers.ListField()


class ReadOddsDetailSerializer(general_serializers.OddsDetailBaseSerializer):
    # region                -----Metadata-----
    class Meta(general_serializers.OddsDetailBaseSerializer.Meta):
        fields = general_serializers.OddsDetailBaseSerializer.Meta.fields + ["value"]

    # endregion


class ReadOddsSerializer(general_serializers.OddsBaseSerializer):
    odds_detail = ReadOddsDetailSerializer(many=True)

    # region                -----Metadata-----
    class Meta(general_serializers.OddsBaseSerializer.Meta):
        fields = general_serializers.OddsBaseSerializer.Meta.fields + [
            "name",
            "odds_detail",
        ]

    # endregion


class ReadBetSerializer(general_serializers.BetBaseSerializer):
    odds = ReadOddsSerializer(many=True)

    # region                -----Metadata-----
    class Meta(general_serializers.BetBaseSerializer.Meta):
        fields = general_serializers.BetBaseSerializer.Meta.fields + [
            "status",
            "type",
            "date_of_game",
            "created_at",
            "game_score",
            "number",
            "commision",
            "commands",
            "event_id",
            "country",
            "result",
            "league",
            "rate",
            "stake",
            "sport",
            "event",
            "odds_value",
            "on",
            "odds",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        date_of_game_str = representation.get("date_of_game")
        if date_of_game_str:
            representation["date_of_game"] = self.to_iso_string(date_of_game_str)

        created_at_str = representation.get("created_at")
        if created_at_str:
            representation["created_at"] = self.to_iso_string(created_at_str)

        return representation

    def to_iso_string(self, date_str):
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
        except ValueError:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y %H:%M")
        return date_obj.isoformat()


class ReadTradeSerializer(general_serializers.BetBaseSerializer):
    class Meta:
        model = Trade
        fields = [
            "opened",
            "closed",
            "traiding_pair",
            "tp_sl",
            "deposit",
            "closing_pnl",
            "direction",
            "orders_type",
            "fee",
            "closing_fee",
            "opening_fee",
        ]
