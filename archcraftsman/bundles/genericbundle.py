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

from typing import Optional

from archcraftsman.base import execute, print_sub_step
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import _


class GenericBundle(Bundle):
    """
    GenericBundle class.
    """

    prompt_str: str
    help_str: Optional[str]
    resume: str
    packages_list: list[str]
    commands_list: list[str]

    def prompt(self) -> str:
        return _(self.prompt_str)

    def help(self) -> Optional[str]:
        return _(self.help_str)

    def packages(self) -> list[str]:
        return [] if self.packages_list is None else self.packages_list

    def print_resume(self):
        print_sub_step(_(self.resume))

    def configure(self):
        if self.commands_list is None:
            return
        for command in self.commands_list:
            execute(f'arch-chroot /mnt bash -c "{command}"')
