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
The yay bundle module
"""

import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.i18n
import archcraftsman.options

_ = archcraftsman.i18n.translate


class Yay(archcraftsman.bundles.bundle.Bundle):
    """
    The Yay class.
    """

    def __init__(self):
        super().__init__(archcraftsman.options.ShellBundles.YAY)

    def packages(self) -> list[str]:
        return ["yay"]

    def is_aur(self) -> bool:
        return True

    def print_resume(self):
        archcraftsman.base.print_sub_step(_("Install YAY."))

    def configure(self):
        if archcraftsman.base.is_root():
            archcraftsman.base.print_error(
                _("You must not be root to install yay."), do_pause=False
            )
            return
        archcraftsman.base.execute("git clone https://aur.archlinux.org/yay")
        archcraftsman.base.execute("cd yay; makepkg -si; cd -; rm -rf yay")
