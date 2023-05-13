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

import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.i18n
import archcraftsman.options

_ = archcraftsman.i18n.translate


class SystemdNet(archcraftsman.bundles.bundle.Bundle):
    """
    Grml ZSH config class.
    """

    def __init__(self):
        super().__init__(archcraftsman.options.Network.SYSTEMD)

    def packages(self) -> list[str]:
        return ["systemd-resolvconf"]

    def print_resume(self):
        archcraftsman.base.print_sub_step(_("Enable systemd network stack."))

    def configure(self):
        archcraftsman.base.execute(
            "ln -sf /run/systemd/resolve/stub-resolv.conf /mnt/etc/resolv.conf"
        )
        archcraftsman.base.execute("cp -r /etc/systemd/network /mnt/etc/systemd/")
        archcraftsman.base.execute("systemctl enable systemd-networkd", chroot=True)
        archcraftsman.base.execute("systemctl enable systemd-resolved", chroot=True)
