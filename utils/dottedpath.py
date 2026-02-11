# region				-----Internal Imports-----
import typing

# endregion


def dottedpath(data: typing.Dict, path: str) -> typing.Any:
    value = data
    for key in path.split("."):
        if isinstance(value, dict):
            value = value.get(key, {})
        else:
            return None
    return value
