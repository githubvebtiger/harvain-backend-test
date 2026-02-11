import typing

# region				-----External Imports-----
from django import http as django_http
from django import utils as django_utils

# endregion

# region				-----Internal Imports-----
# endregion


def permissions(permission_classes: typing.Iterable) -> typing.Callable:
    def wrapper_of_wrapper(function: typing.Callable) -> typing.Callable:
        def default_wrapper(
            self, request: django_http.HttpRequest, *args, **kwargs
        ) -> typing.Callable:
            # * Override view permissions with the new one
            self.permission_classes = permission_classes
            self.check_permissions(request=request)

            return function(self, request=request, *args, **kwargs)

        return default_wrapper

    return wrapper_of_wrapper


def change_output(
    serializer: typing.Callable, on_methods: typing.Iterable
) -> typing.Callable:
    def wrapper_of_wrapper(function: typing.Callable) -> typing.Callable:
        def default_wrapper(
            self, instance: typing.Any, *args, **kwargs
        ) -> typing.Callable:
            # * Check whether to change output serializer
            methods = [self.context["request"].method, "__all__"]
            if any(method in on_methods for method in methods):
                return function(self, instance=instance, *args, **kwargs)
            output_serializer = serializer(instance=instance, *args, **kwargs)
            return output_serializer.data

        return default_wrapper

    return wrapper_of_wrapper


def make_translatable(function: typing.Callable) -> typing.Callable:
    def default_wrapper(
        self, request: django_http.HttpRequest, *args, **kwargs
    ) -> typing.Callable:
        # * Find out current thread language from request
        language = django_utils.translation.get_language_from_request(
            request=request, check_path=True
        )

        # * Activate current language with manager
        django_utils.translation.activate(language)
        return function(self, request=request, *args, **kwargs)

    return default_wrapper
