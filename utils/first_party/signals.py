import typing
from collections import abc
from functools import wraps

# region				-----External Imports-----
from django.db import transaction

# endregion


def after_transaction_commit(function: typing.Callable) -> typing.Callable:
    def decorator(*args, **kwargs) -> None:
        transaction.on_commit(lambda: function(*args, **kwargs))

    return decorator


def multiple_sender_receiver(
    signal: typing.Callable, senders: typing.List, *args, **kwargs
) -> typing.Callable:
    def decorator(receiver_func: typing.Callable) -> typing.Callable:
        for sender in senders:
            if isinstance(signal, abc.Iterable):
                for sign in signal:
                    sign.connect(receiver_func, sender=sender, *args, **kwargs)
            else:
                signal.connect(receiver_func, sender=sender, *args, **kwargs)
        return receiver_func

    return decorator


def disable_for_loaddata(signal_handler):
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs.get("raw"):
            return
        signal_handler(*args, **kwargs)

    return wrapper


def inherited_sender_receiver(
    sender: typing.Type[object],
    excludes: typing.Iterable,
    signal: typing.Callable,
    *args,
    **kwargs
) -> typing.Callable:
    def inheritors() -> typing.Set:
        subclasses = set()
        parents = [sender]

        for parent in parents:
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    parents.append(child)

        for exclude in excludes:
            subclasses.remove(exclude)

        return subclasses

    def decorator(receiver_function: typing.Callable) -> typing.Callable:
        for sender in inheritors():
            if isinstance(signal, abc.Iterable):
                for s in signal:
                    s.connect(receiver_function, sender=sender, *args, **kwargs)
            else:
                signal.connect(receiver_function, sender=sender, *args, **kwargs)
        return receiver_function

    return decorator
