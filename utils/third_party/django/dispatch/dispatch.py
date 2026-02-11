# region				-----External Imports-----
import typing

# region				-----Internal Imports-----
from . import utils

# endregion

# endregion


def inherited_sender_receiver(
    sender: typing.Type[object], signals: typing.Iterable, exclude: list = [], **kwargs
) -> typing.Callable:
    # * Find all subclasses from inheritance tree
    senders = utils.find_subclasses(exclude=exclude, parent=sender)
    return multiple_sender_receiver(signals=signals, senders=senders, **kwargs)


def multiple_sender_receiver(
    signals: typing.Iterable, senders: typing.Iterable, **kwargs
) -> typing.Callable:
    def default_wrapper(function: typing.Callable) -> typing.Callable:
        for sender in senders:
            # * Find out how to connect signals
            if isinstance(signals, (list, tuple)):
                for signal in signals:
                    signal.connect(receiver=function, sender=sender, **kwargs)
            else:
                signals.connect(receiver=function, sender=sender, **kwargs)

    return default_wrapper
