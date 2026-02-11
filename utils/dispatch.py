# region				-----External Imports-----
import typing

# endregion


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
