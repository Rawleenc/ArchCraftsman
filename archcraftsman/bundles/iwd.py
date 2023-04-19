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
The network manager bundle module
"""

from archcraftsman.base import execute, print_sub_step
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.bundles.systemdnet import SystemdNet
from archcraftsman.i18n import _
from archcraftsman.options import BundleTypes


class Iwd(Bundle):
    """
    Grml ZSH config class.
    """

    def packages(self) -> list[str]:
        packages = ["iwd"]
        return packages

    def print_resume(self):
        print_sub_step(_("Install Iwd."))
        SystemdNet(self.name, BundleTypes.OTHER).print_resume()

    def configure(self):
        execute('arch-chroot /mnt bash -c "systemctl enable iwd.service"')
        SystemdNet(self.name, BundleTypes.OTHER).configure()
