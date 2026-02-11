# region				-----External Imports-----
import typing

# endregion

# region				-----Internal Imports-----
# endregion


def find_subclasses(
    parent: typing.Type[object], exclude: typing.Iterable
) -> typing.Iterable:
    inheritors = set()
    parents = [parent]

    for parent in parents:
        for child in parent.__subclasses__():
            inheritors.add(child)
            parents.append(child)

    for child in exclude:
        inheritors.remove(child)

    return inheritors
