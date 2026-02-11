import six
from rest_framework import serializers as rest_serializers

# region				-----External Imports-----
from rest_framework_simplejwt import tokens as simple_tokens

# region				-----Internal Imports-----
from ...general import serializers as general_serializers

# endregion

# endregion


class ReadTransactionSerializer(general_serializers.TransactionBaseSerializer):
    # region                -----Metadata-----
    class Meta(general_serializers.TransactionBaseSerializer.Meta):
        fields = general_serializers.TransactionBaseSerializer.Meta.fields + [
            "amount",
            "comment",
            "system",
            "status",
            "created_at",
        ]

    # endregion
