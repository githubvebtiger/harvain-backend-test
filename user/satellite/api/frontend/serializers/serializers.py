import typing

import six
from django.core.validators import MinLengthValidator
from drf_spectacular import utils as drf_utils
from rest_framework import serializers as rest_serializers
from rest_framework_simplejwt import tokens as simple_tokens

# region				-----External Imports-----
from utils.third_party.rest_framework import decorators as utils_decorators

from ..... import models as satellite_models
from ..... import validators as user_validators

# region				-----Internal Imports-----
from ...general import serializers as general_serializers

# endregion

# endregion


@drf_utils.extend_schema_serializer(exclude_fields=["id"])
class SatelliteAuthSerializer(general_serializers.SatelliteBaseSerializer):
    class Meta(general_serializers.SatelliteBaseSerializer.Meta):
        fields = general_serializers.SatelliteBaseSerializer.Meta.fields + ["password"]


class SatelliteClientSerializer(general_serializers.SatelliteBaseSerializer):
    class Meta(general_serializers.SatelliteBaseSerializer.Meta):
        fields = general_serializers.SatelliteBaseSerializer.Meta.fields + [
            "block_balance",
            "active_balance",
            "withdrawal",
            "order",
        ]


class ReadSatelliteSerializer(general_serializers.SatelliteBaseSerializer):
    tokens = rest_serializers.SerializerMethodField()
    is_data_filled = rest_serializers.SerializerMethodField()
    can_auto_unblock = rest_serializers.SerializerMethodField()

    # region                -----Metadata-----
    class Meta(general_serializers.SatelliteBaseSerializer.Meta):
        fields = general_serializers.SatelliteBaseSerializer.Meta.fields + [
            "name",
            "city",
            "country",
            "address",
            "username",
            "last_name",
            "born",
            "phone",
            "email",
            "invitation_code",
            "allow_password_update",
            "allow_password_update",
            "block_balance",
            "active_balance",
            "withdrawal",
            "tokens",
            "email_verified",
            "document_verified",
            "document_verified_at",
            "verify_status",
            "is_data_filled",
            "can_auto_unblock",
            "blocked",
            "created_at",
            "deposit",
            "deposit_time",
            "migration_time",
            "second_migration_time",
        ]

    # endregion

    def get_tokens(self, user):
        tokens = simple_tokens.RefreshToken.for_user(user)
        refresh = six.text_type(tokens)
        access = six.text_type(tokens.access_token)
        data = {"refresh": refresh, "access": access}
        return data
    
    def get_is_data_filled(self, obj):
        required_fields = [
            "name",
            "last_name",
            "country",
            "city",
            "address",
            "born",
            "phone",
            "email",
        ]
        for field in required_fields:
            value = getattr(obj, field, None)
            if value in [None, ""]:
                return False
        return True
    
    def get_can_auto_unblock(self, obj):
        """Determine if account can be auto-unblocked upon verification"""
        if not obj.blocked:
            return False
        
        # If verified before blocking, cannot auto-unblock
        if (obj.document_verified_at and 
            obj.migration_time and
            obj.document_verified_at < obj.migration_time):
            return False
        
        return True


class WriteSatelliteSerializer(general_serializers.SatelliteBaseSerializer):
    last_name = rest_serializers.CharField(
        max_length=15,
        allow_null=True,
        allow_blank=True,
        validators=[user_validators.latin_numeric_validator],
        required=False,
    )
    name = rest_serializers.CharField(
        max_length=15,
        allow_null=True,
        allow_blank=True,
        validators=[user_validators.latin_numeric_validator],
        required=False,
    )
    country = rest_serializers.CharField(max_length=20, allow_null=True, allow_blank=True, required=False)
    city = rest_serializers.CharField(max_length=20, allow_null=True, allow_blank=True, required=False)
    address = rest_serializers.CharField(max_length=255, allow_null=True, allow_blank=True, required=False)
    born = rest_serializers.DateField(allow_null=True, required=False)

    # region                -----Metadata-----
    class Meta(general_serializers.SatelliteBaseSerializer.Meta):
        fields = general_serializers.SatelliteBaseSerializer.Meta.fields + [
            "last_name",
            "name",
            "phone",
            "country",
            "city",
            "address",
            "born",
            "email",
        ]

    # endregion

    @utils_decorators.change_output(serializer=ReadSatelliteSerializer, on_methods=["UPDATE"])
    def to_representation(self, instance):
        return super(WriteSatelliteSerializer, self).to_representation(instance=instance)


class WriteSatellitePasswordSerializer(rest_serializers.ModelSerializer):
    new_password = rest_serializers.CharField(
        required=True,
        validators=[MinLengthValidator(8), user_validators.password_validator],
    )
    new_password2 = rest_serializers.CharField(
        required=True,
        validators=[MinLengthValidator(8), user_validators.password_validator],
    )
    old_password = rest_serializers.CharField(required=True)

    # region                -----Metadata-----
    class Meta(object):
        fields = ["new_password", "new_password2", "old_password"]
        model = satellite_models.Satellite

    # endregion

    # region      -----Internal Methods-----
    def validate(self, attrs) -> typing.Dict:
        if not self.context["request"].user.allow_password_update:
            raise rest_serializers.ValidationError({"old_password": "You can't update password."})

        if attrs["new_password"] != attrs["new_password2"]:
            raise rest_serializers.ValidationError(
                {
                    "new_password": "Passwords don't match.",
                    "new_password2": "Passwords don't match.",
                }
            )
        if attrs["new_password"] == attrs["old_password"]:
            raise rest_serializers.ValidationError({"old_password": "The old password cannot match the new one."})
        return attrs

    # endregion

