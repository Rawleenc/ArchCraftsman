"""
The I18n management singleton module
"""
from argparse import Namespace
from threading import Lock


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
    args: Namespace = None

    def __init__(self, args: Namespace = None) -> None:
        self.args = args

    def test(self) -> bool:
        """
        Check if the installer is in fake test mode.
        :return:
        """
        return self.args.test
