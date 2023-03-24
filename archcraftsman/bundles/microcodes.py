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
The microcodes auto-installation bundle module
"""
import re
from typing import Optional

from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import I18n
from archcraftsman.options import Bundles
from archcraftsman.systeminfo import SystemInfo
from archcraftsman.utils import print_sub_step, execute

_ = I18n().gettext


class Microcodes(Bundle):
    """
    The Microcodes class.
    """

    def __init__(self):
        super().__init__(Bundles.MICROCODES)
        cpu_info_vendor = execute(
            'grep </proc/cpuinfo "vendor" | uniq', force=True, capture_output=True
        ).output
        if cpu_info_vendor:
            self.microcode_name = re.sub("\\s+", "", cpu_info_vendor).split(":")[1]
        else:
            self.microcode_name = None

    def packages(self, system_info: SystemInfo) -> list[str]:
        if self.microcode_name == "GenuineIntel":
            return ["intel-ucode"]
        if self.microcode_name == "AuthenticAMD":
            return ["amd-ucode"]
        return []

    def microcode_img(self) -> Optional[str]:
        """
        The microcode img file name retrieving method.
        """
        if self.microcode_name == "GenuineIntel":
            return "/intel-ucode.img"
        if self.microcode_name == "AuthenticAMD":
            return "/amd-ucode.img"
        return None

    def print_resume(self):
        if self.microcode_name in {"GenuineIntel", "AuthenticAMD"}:
            print_sub_step(_("Microcodes to install : %s") % self.microcode_name)
