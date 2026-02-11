# region				-----External Imports-----
from rest_framework import serializers as rest_serializers

# region				-----Internal Imports-----
from .... import models as finance_models

# endregion

# endregion


class TransactionBaseSerializer(rest_serializers.ModelSerializer):
    # region                -----Metadata-----
    class Meta(object):
        fields = ["id", "type"]
        model = finance_models.Transaction

    # endregion
