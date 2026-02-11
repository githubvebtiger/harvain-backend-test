import logging
import traceback
import typing
from typing import Callable, Dict

import jwt
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect

# region				-----External Imports-----
from rest_framework.authtoken.models import Token

import user

# endregion

# region			  -----Supporting Variables-----
logger = logging.getLogger(__file__)
# endregion


class SaveIPMiddleware(object):
    def __init__(self, get_response: typing.Callable) -> None:
        self._get_response = get_response

    def _get_ip(self, request) -> str:
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0]

        return request.META.get("REMOTE_ADDR")

    def __call__(self, request: typing.Dict) -> typing.Dict:
        response = self._get_response(request)
        normalized_path = request.path.rstrip("/")

        if (
            normalized_path == "/api/frontend/token/satellite"
            or normalized_path == "/api/frontend/token/client"
        ) and response.status_code == 200:
            current_ip = self._get_ip(request)

            try:
                if not response.data.get("id"):
                    # Decode JWT token to extract user_id
                    payload = jwt.decode(
                        jwt=response.data.get("access"),
                        key=settings.SECRET_KEY,
                        algorithms=["HS256"],
                    )
                    current_user = payload.get("user_id")

                    if not current_user:
                        logger.warning("JWT token missing user_id in payload")
                        return response
                else:
                    current_user = response.data.get("id")

                # Log entrance only if we successfully got user_id
                if current_user:
                    user.user.models.Entrance.objects.create(
                        user_id=current_user, ip=current_ip
                    )
            except (jwt.DecodeError, jwt.InvalidTokenError) as e:
                # Log JWT errors but don't break the request
                logger.warning(f"Invalid JWT token in SaveIPMiddleware: {e}")
            except (KeyError, TypeError, AttributeError) as e:
                # Log unexpected errors but don't break the request
                logger.error(f"Unexpected error in SaveIPMiddleware: {e}")
            except Exception as e:
                # Catch-all for any other errors to prevent middleware from breaking
                logger.error(f"Critical error in SaveIPMiddleware: {e}", exc_info=True)

        return response
