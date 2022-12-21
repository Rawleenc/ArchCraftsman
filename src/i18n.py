"""
The I18n management singleton module
"""
import gettext
from threading import Lock


class I18nMeta(type):
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


class I18n(metaclass=I18nMeta):
    """
    The singleton implementation containing the translation method to use.
    """
    gettext_method = None

    def __init__(self) -> None:
        self.gettext_method = gettext.gettext

    def update_method(self, method):
        """
        Update the translation method.
        :param method:
        :return:
        """
        self.gettext_method = method
        return self.gettext_method

    def gettext(self, message):
        """
        Translate the given text with the translation method.
        :param message:
        :return:
        """
        return self.gettext_method(message)
