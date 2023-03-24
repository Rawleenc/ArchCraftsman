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
The main file systems bundle module
"""
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import I18n
from archcraftsman.systeminfo import SystemInfo
from archcraftsman.utils import print_sub_step

_ = I18n().gettext


def get_main_file_systems() -> list[str]:
    """
    The method to get the package list of the main file systems group.
    """
    return [
        "btrfs-progs",
        "dosfstools",
        "exfatprogs",
        "f2fs-tools",
        "e2fsprogs",
        "jfsutils",
        "nilfs-utils",
        "ntfs-3g",
        "reiserfsprogs",
        "udftools",
        "xfsprogs",
    ]


class MainFileSystems(Bundle):
    """
    The main file systems class.
    """

    def packages(self, system_info: SystemInfo) -> list[str]:
        return get_main_file_systems()

    def print_resume(self):
        print_sub_step(_("Install main file systems support."))
