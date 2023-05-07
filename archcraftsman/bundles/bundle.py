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
The generic bundle blueprint module
"""


class Bundle:
    """
    A class to represent a bootloader.
    """

    def __init__(self, name: str = "") -> None:
        self.name = name

    def prompt(self) -> str:
        """
        Bundle's main prompt retrieving method.
        """
        return ""

    def help(self) -> str:
        """
        Bundle's help retrieving method.
        """
        return ""

    def packages(self) -> list[str]:
        """
        Bundle's packages retrieving method.
        """
        return []

    def is_aur(self) -> bool:
        """
        Is Bundle AUR based.
        """
        return False

    def prompt_extra(self):
        """
        Bundle's extra options prompting method.
        """

    def print_resume(self):
        """
        Bundle's print resume method.
        """

    def configure(self):
        """
        Bundle configuration method.
        """
