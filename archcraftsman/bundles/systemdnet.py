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
The systemd network bundle module
"""

from archcraftsman.base import execute, print_sub_step
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import _


class SystemdNet(Bundle):
    """
    Grml ZSH config class.
    """

    def packages(self) -> list[str]:
        return ["systemd-resolvconf"]

    def print_resume(self):
        print_sub_step(_("Enable systemd network stack."))

    def configure(self):
        execute("ln -sf /run/systemd/resolve/stub-resolv.conf /mnt/etc/resolv.conf")
        execute("cp -r /etc/systemd/network /mnt/etc/systemd/")
        execute('arch-chroot /mnt bash -c "systemctl enable systemd-networkd"')
        execute('arch-chroot /mnt bash -c "systemctl enable systemd-resolved"')
