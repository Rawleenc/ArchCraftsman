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
import typing

import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.i18n
import archcraftsman.options

_ = archcraftsman.i18n.translate


class Microcodes(archcraftsman.bundles.bundle.Bundle):
    """
    The Microcodes class.
    """

    def __init__(self):
        super().__init__(archcraftsman.options.Bundles.MICROCODES)
        self._cpu_info_vendor = archcraftsman.base.execute(
            'grep </proc/cpuinfo "vendor" | uniq', force=True, capture_output=True
        ).output
        self._microcode_name = (
            re.sub("\\s+", "", self._cpu_info_vendor).split(":")[1]
            if self._cpu_info_vendor
            else ""
        )

    def packages(self) -> list[str]:
        if self._microcode_name == "GenuineIntel":
            return ["intel-ucode"]
        if self._microcode_name == "AuthenticAMD":
            return ["amd-ucode"]
        return []

    def microcode_img(self) -> typing.Optional[str]:
        """
        The microcode img file name retrieving method.
        """
        if self._microcode_name == "GenuineIntel":
            return "/intel-ucode.img"
        if self._microcode_name == "AuthenticAMD":
            return "/amd-ucode.img"
        return None

    def print_resume(self):
        if self._microcode_name in {"GenuineIntel", "AuthenticAMD"}:
            archcraftsman.base.print_sub_step(
                _("Microcodes to install : %s") % self._microcode_name
            )
