# region				-----Internal Imports-----
from ...general import serializers as general_serializers

# endregion

# region			  -----Supporting Variables-----
# endregion


class ReadRequisitesSerializer(general_serializers.RequisitesBaseSerializer):
    # region                -----Metadata-----
    class Meta(general_serializers.RequisitesBaseSerializer.Meta):
        fields = general_serializers.RequisitesBaseSerializer.Meta.fields + [
            "icon",
            "show",
            "client",
        ]

    # endregion
