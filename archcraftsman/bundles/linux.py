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
All supported linux kernel bundles module
"""
from archcraftsman.base import print_sub_step
from archcraftsman.bundles import bundle
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import _
from archcraftsman.options import Kernels


class LinuxCurrent(bundle.Bundle):
    """
    The Linux current kernel class.
    """

    def __init__(self):
        super().__init__(Kernels.CURRENT)

    def packages(self) -> list[str]:
        return ["linux", "linux-headers"]

    def print_resume(self):
        print_sub_step(_("Install Linux current kernel."))


class LinuxHardened(Bundle):
    """
    The Linux hardened kernel class.
    """

    def __init__(self):
        super().__init__(Kernels.HARDENED)

    def packages(self) -> list[str]:
        return ["linux-hardened", "linux-hardened-headers"]

    def print_resume(self):
        print_sub_step(_("Install Linux hardened kernel."))


class LinuxLts(bundle.Bundle):
    """
    The Linux LTS kernel class.
    """

    def __init__(self):
        super().__init__(Kernels.LTS)

    def packages(self) -> list[str]:
        return ["linux-lts", "linux-lts-headers"]

    def print_resume(self):
        print_sub_step(_("Install Linux LTS kernel."))


class LinuxZen(bundle.Bundle):
    """
    The Linux zen kernel class.
    """

    def __init__(self):
        super().__init__(Kernels.ZEN)

    def packages(self) -> list[str]:
        return ["linux-zen", "linux-zen-headers"]

    def print_resume(self):
        print_sub_step(_("Install Linux zen kernel."))
