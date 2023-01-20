"""
The I18n management singleton module
"""
import gettext
from threading import Lock

from src.globalargs import GlobalArgs


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

    def update_method(self, global_language: str):
        """
        Update the translation method to use according to the global language.
        :param global_language:
        :return:
        """
        if not GlobalArgs().test() and global_language != "EN":
            translation = gettext.translation('ArchCraftsman', localedir='/usr/share/locale',
                                              languages=[global_language.lower()])
            translation.install()
            self.gettext_method = translation.gettext
        return self.gettext_method

    def gettext(self, message):
        """
        Translate the given text with the translation method.
        :param message:
        :return:
        """
        return self.gettext_method(message)
