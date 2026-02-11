import typing

import six
from rest_framework import serializers as rest_serializers

# region				-----External Imports-----
from rest_framework_simplejwt import tokens as simple_tokens

# region				-----Internal Imports-----
from .....satellite.api.frontend import serializers as satellite_serializers
from .... import models as user_models
from ...general import serializers as general_serializers

# endregion

# endregion

# region			  -----Supporting Variables-----
# endregion


class ReadClientSerializer(general_serializers.ClientBaseSerializer):
    tokens = rest_serializers.SerializerMethodField()
    satellites = satellite_serializers.SatelliteClientSerializer(many=True)
    verify_status = rest_serializers.SerializerMethodField()
    can_auto_unblock = rest_serializers.SerializerMethodField()

    # region                -----Metadata-----
    class Meta(general_serializers.ClientBaseSerializer.Meta):
        fields = [
            "username",
            "name",
            "city",
            "country",
            "address",
            "full_name",
            "last_name",
            "born",
            "phone",
            "email",
            "email_verified",
            "document_verified",
            "document_verified_at",
            "verify_status",
            "can_auto_unblock",
            "invitation_code",
            "allow_password_update",
            "allow_password_update",
            "satellites",
            "total_balance",
            "tokens",
        ]

    # endregion

    def to_representation(self, instance: typing.Callable) -> typing.Dict:
        representation = super().to_representation(instance)

        satellites_list = list(representation["satellites"])
        satellite_counter = len(satellites_list)
        satellites = []

        for satellite_index in range(satellite_counter):
            # find satellite index or -1
            satellite_index = next(
                (i for i, satellite in enumerate(satellites_list) if dict(satellite)["order"] == satellite_index + 1),
                -1,
            )

            if satellite_index == -1:
                satellites.append(satellites_list[0])
                del satellites_list[0]
            else:
                satellites.append(satellites_list[satellite_index])
                del satellites_list[satellite_index]

        representation["satellites"] = satellites
        return representation

    def get_tokens(self, user):
        tokens = simple_tokens.RefreshToken.for_user(user)
        refresh = six.text_type(tokens)
        access = six.text_type(tokens.access_token)
        data = {"refresh": refresh, "access": access}
        return data

    def get_verify_status(self, instance):
        return instance.verify_status
    
    def get_can_auto_unblock(self, obj):
        """Determine if account can be auto-unblocked upon verification"""
        # Check if this is a satellite (has blocked attribute)
        if not hasattr(obj, 'blocked'):
            return False
            
        if not obj.blocked:
            return False
        
        # If already document_verified, cannot auto-unblock (was verified before blocking)
        if obj.document_verified:
            return False
        
        return True


class CreateClientSerializer(rest_serializers.ModelSerializer):
    class Meta(object):
        fields = ["id", "username", "full_name", "phone", "email", "country", "password_visible", "is_active"]
        model = user_models.Client


class CreateSupportTicketSerializer(rest_serializers.ModelSerializer):
    class Meta(object):
        fields = ["full_name", "email", "account_number", "subject", "description"]
        model = user_models.SupportTicket


class CreatePaymentSerializer(rest_serializers.ModelSerializer):
    class Meta(object):
        fields = ["full_name", "total_price", "requisite", "to_be_paid", "user"]
        model = user_models.Payment


class WriteClientSerializer(general_serializers.ClientBaseSerializer):
    class Meta(general_serializers.ClientBaseSerializer.Meta):
        fields = general_serializers.ClientBaseSerializer.Meta.fields + [
            "last_name",
            "name",
            "phone",
            "country",
            "city", 
            "address",
            "born",
            "email",
        ]

    def to_representation(self, instance):
        return ReadClientSerializer(instance).data


class RetrievePlanSerializer(rest_serializers.ModelSerializer):
    class Meta(object):
        fields = ["full_name", "total_price", "requisite", "to_be_paid"]
        model = user_models.PricingPlan
