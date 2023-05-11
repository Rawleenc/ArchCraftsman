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
The plasma bundle module
"""

from archcraftsman import info
from archcraftsman.base import execute, print_sub_step
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import _
from archcraftsman.options import Bundles, Desktops
from archcraftsman.utils import prompt_bool


class Plasma(Bundle):
    """
    Bundle class.
    """

    def __init__(self):
        super().__init__(Desktops.PLASMA)
        self.minimal = False
        self.plasma_wayland = False

    def packages(self) -> list[str]:
        packages = [
            "plasma",
            "xorg-server",
            "alsa-utils",
            "pulseaudio",
            "pulseaudio-alsa",
            "xdg-desktop-portal",
            "xdg-desktop-portal-kde",
        ]
        if self.plasma_wayland:
            packages.extend(["plasma-wayland-session", "qt5-wayland"])
            if info.ai.system_info.others() and Bundles.NVIDIA in [
                bundle.name for bundle in info.ai.system_info.others()
            ]:
                packages.append("egl-wayland")
            if self.minimal is not True:
                packages.append("kde-applications")
            else:
                packages.append("konsole")

        return packages

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % "SDDM")
        if self.minimal:
            print_sub_step(_("Install a minimal environment."))
        if self.plasma_wayland:
            print_sub_step(_("Install Wayland support for the plasma session."))

    def prompt_extra(self):
        self.minimal = prompt_bool(
            _("Install a minimal environment ?"),
            default=False,
            help_msg=_(
                "If yes, the script will not install any extra packages, only base packages."
            ),
        )
        self.plasma_wayland = prompt_bool(
            _("Install Wayland support for the plasma session ?"), default=False
        )

    def configure(self):
        execute("systemctl enable sddm", chroot=True)
        info.ai.pre_launch_info.setup_chroot_keyboard()
