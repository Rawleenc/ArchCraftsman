import gettext
from threading import Lock


class I18nMeta(type):
    """
    This is a thread-safe implementation of Singleton.
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
    gettext_method = None
    """
    We'll use this property to prove that our Singleton really works.
    """

    def __init__(self) -> None:
        self.gettext_method = gettext.gettext

    def update_method(self, method):
        self.gettext_method = method
        return self.gettext_method

    def gettext(self, message):
        return self.gettext_method(message)
