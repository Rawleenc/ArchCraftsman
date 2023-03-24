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
