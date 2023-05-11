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
The TOML valued generic bundle module
"""

import tomllib
from importlib.resources import files
from typing import Optional

from archcraftsman.base import execute, print_sub_step
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import _t


class GenericBundle(Bundle):
    """
    GenericBundle class.
    """

    _prompt: str
    _resume: str
    _help: Optional[str]
    _packages: list[str]
    _commands: list[str]

    def __init__(self, name: str = ""):
        super().__init__(name)
        generic_bundle_config = files("archcraftsman.bundles.configs").joinpath(
            f"{name}.toml"
        )
        if not generic_bundle_config.is_file():
            data = None
        else:
            with open(str(generic_bundle_config), "rb") as config_file:
                data = tomllib.load(config_file)
        if data:
            self._prompt = data.get("prompt", f"Do you want to install {name} ?")
            self._resume = data.get("resume", f"Install {name}.")
            self._help = data.get("help", None)
            self._packages = data.get("packages", [])
            self._commands = data.get("commands", [])

    def format_str(self, string: str) -> str:
        """
        Format a string with the bundle's data.
        """
        string = string.format(packages=",".join(self.packages()))
        return string

    def prompt(self) -> str:
        return self.format_str(_t(self._prompt))

    def help(self) -> str:
        return self.format_str(_t(self._help)) if self._help else ""

    def packages(self) -> list[str]:
        return [] if self._packages is None else self._packages

    def print_resume(self):
        print_sub_step(self.format_str(_t(self._resume)))

    def configure(self):
        if self._commands is None:
            return
        for command in self._commands:
            execute(command, chroot=True)
