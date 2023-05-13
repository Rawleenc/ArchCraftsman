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
The gnome bundle module
"""

import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.i18n
import archcraftsman.info
import archcraftsman.options
import archcraftsman.utils

_ = archcraftsman.i18n.translate


class Gnome(archcraftsman.bundles.bundle.Bundle):
    """
    Bundle class.
    """

    def __init__(self):
        super().__init__(archcraftsman.options.Desktops.GNOME)
        self.minimal = False

    def packages(self) -> list[str]:
        packages = [
            "gnome",
            "alsa-utils",
            "pulseaudio",
            "pulseaudio-alsa",
            "xdg-desktop-portal",
            "xdg-desktop-portal-gnome",
            "qt5-wayland",
            "gst-plugin-pipewire",
        ]
        if self.minimal is not True:
            packages.append("gnome-extra")
        return packages

    def print_resume(self):
        archcraftsman.base.print_sub_step(_("Desktop environment : %s") % self.name)
        archcraftsman.base.print_sub_step(_("Display manager : %s") % "GDM")

    def prompt_extra(self):
        self.minimal = archcraftsman.utils.prompt_bool(
            _("Install a minimal environment ?"),
            default=False,
            help_msg=_(
                "If yes, the script will not install any extra packages, only base packages."
            ),
        )

    def configure(self):
        archcraftsman.base.execute("systemctl enable gdm", chroot=True)
        archcraftsman.info.ai.pre_launch_info.setup_chroot_keyboard()
