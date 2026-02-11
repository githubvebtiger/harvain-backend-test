# region				-----External Imports-----
import typing

# endregion

# region				-----Internal Imports-----
# endregion


def disable_for_loadout(function: typing.Callable) -> typing.Callable:
    def default_wrapper(instance: typing.Type[object], **kwargs) -> typing.Callable:
        # * Find out whether to call signal
        if not kwargs.get("raw"):
            return function(instance=instance, **kwargs)

    return default_wrapper
