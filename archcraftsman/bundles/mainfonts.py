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
The main fonts bundle module
"""
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import I18n
from archcraftsman.systeminfo import SystemInfo
from archcraftsman.utils import print_sub_step

_ = I18n().gettext


def get_main_fonts() -> list[str]:
    """
    The method to get the package list of the main fonts group.
    """
    return [
        "gnu-free-fonts",
        "noto-fonts",
        "ttf-bitstream-vera",
        "ttf-dejavu",
        "ttf-hack",
        "ttf-droid",
        "ttf-fira-code",
        "ttf-fira-mono",
        "ttf-fira-sans",
        "ttf-font-awesome",
        "ttf-inconsolata",
        "ttf-input",
        "ttf-liberation",
        "ttf-nerd-fonts-symbols-2048-em",
        "ttf-opensans",
        "ttf-roboto",
        "ttf-roboto-mono",
        "ttf-ubuntu-font-family",
        "ttf-jetbrains-mono",
        "otf-font-awesome",
        "noto-fonts-emoji",
        "inter-font",
    ]


class MainFonts(Bundle):
    """
    The main fonts class.
    """

    def packages(self, system_info: SystemInfo) -> list[str]:
        return get_main_fonts()

    def print_resume(self):
        print_sub_step(_("Install a set of main fonts."))
