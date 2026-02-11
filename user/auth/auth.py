from rest_framework_simplejwt.authentication import JWTAuthentication

from ..client import models as client_models


class CustomJWTAuthentication(JWTAuthentication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_class = client_models.Client
