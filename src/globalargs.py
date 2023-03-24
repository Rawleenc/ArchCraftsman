"""
The I18n management singleton module
"""
from argparse import Namespace
from threading import Lock
from typing import Optional


class GlobalArgsMeta(type):
    """
    Thread-safe implementation of Singleton to manage translations.
    """

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class GlobalArgs(metaclass=GlobalArgsMeta):
    """
    The singleton implementation containing the translation method to use.
    """

    def __init__(self, args: Optional[Namespace] = None) -> None:
        if args:
            self.args = args

    def is_call_ok(self) -> bool:
        """
        Check if the installer is called correctly.
        """
        return self.args and (self.install() or self.shell())

    def install(self) -> bool:
        """
        Check if the installer is in installation mode.
        """
        return self.args and self.args.install

    def test(self) -> bool:
        """
        Check if the installer is in fake test mode.
        """
        return self.args and self.args.test

    def shell(self) -> bool:
        """
        Check if the installer is in shell mode.
        """
        return self.args and self.args.shell
