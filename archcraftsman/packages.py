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
The packages management singleton module
"""
import readline
from threading import Lock

from archcraftsman.i18n import I18n
from archcraftsman.utils import prompt_ln, print_error, execute, glob_completer

_ = I18n().gettext


class PackagesMeta(type):
    """
    Thread-safe implementation of Singleton to store all archlinux packages.
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


class Packages(metaclass=PackagesMeta):
    """
    The singleton implementation containing all archlinux packages and autocompleted prompt method.
    """

    packages: set[str]

    def __init__(self) -> None:
        self.packages = set(
            execute(
                "pacman -Sl | awk '{print $2}'",
                check=False,
                force=True,
                capture_output=True,
            )
            .output.strip()
            .split("\n")
        )

    def exist(self, package: str) -> bool:
        """
        A method to check if a package exist.
        """
        return package in self.packages

    def ask_packages(self) -> set[str]:
        """
        A method to ask the user for more packages to install.
        """
        readline.set_completer(
            lambda text, state: (
                [
                    package
                    for package in self.packages
                    if (text and package.startswith(text))
                ]
            )[state]
        )

        pkgs_select_ok = False
        more_pkgs = set()
        while not pkgs_select_ok:
            more_pkgs = set()
            more_pkgs_str = prompt_ln(
                _(
                    "Install more packages ? (type extra packages full names, example : 'htop neofetch', "
                    "leave blank if none) : "
                )
            )
            pkgs_select_ok = True
            if more_pkgs_str:
                for pkg in more_pkgs_str.split():
                    if not self.exist(pkg):
                        pkgs_select_ok = False
                        print_error(_("Package %s doesn't exist.") % pkg)
                        break
                    more_pkgs.add(pkg)

        readline.set_completer(glob_completer)
        return more_pkgs
