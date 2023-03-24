# ArchCraftsman, The careful yet very fast Arch Linux Craftsman.
# Copyright (C) 2023 Rawleenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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

    def __init__(self) -> None:
        self.gettext_method = gettext.gettext

    def update_method(self, global_language: str):
        """
        Update the translation method to use according to the global language.
        """
        if global_language != "EN":
            translation = gettext.translation(
                "ArchCraftsman",
                localedir="/usr/share/locale",
                languages=[global_language.lower()],
            )
            translation.install()
            self.gettext_method = translation.gettext
        return self.gettext_method

    def gettext(self, message):
        """
        Translate the given text with the translation method.
        """
        return self.gettext_method(message)
