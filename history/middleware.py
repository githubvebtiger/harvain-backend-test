import threading

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

_thread_locals = threading.local()


def get_current_user():
    return getattr(_thread_locals, "user", None)


class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            jwt_authenticator = JWTAuthentication()
            user, _ = jwt_authenticator.authenticate(request)
            request.user = user
        except (AuthenticationFailed, TypeError):
            pass

        _thread_locals.user = request.user
        response = self.get_response(request)
        return response
