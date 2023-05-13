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

import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.bundles.systemdnet
import archcraftsman.i18n
import archcraftsman.options

_ = archcraftsman.i18n.translate


class Iwd(archcraftsman.bundles.bundle.Bundle):
    """
    Iwd config class.
    """

    def __init__(self):
        super().__init__(archcraftsman.options.Network.IWD)

    def packages(self) -> list[str]:
        packages = ["iwd"]
        return packages

    def print_resume(self):
        archcraftsman.base.print_sub_step(_("Install Iwd."))
        archcraftsman.bundles.systemdnet.SystemdNet().print_resume()

    def configure(self):
        archcraftsman.base.execute("systemctl enable iwd.service", chroot=True)
        archcraftsman.bundles.systemdnet.SystemdNet().configure()
