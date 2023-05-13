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
The budgie bundle module
"""

import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.i18n
import archcraftsman.info
import archcraftsman.options
import archcraftsman.utils

_ = archcraftsman.i18n.translate


class Budgie(archcraftsman.bundles.bundle.Bundle):
    """
    Bundle class.
    """

    def __init__(self):
        super().__init__(archcraftsman.options.Desktops.BUDGIE)
        self.display_manager = True

    def packages(self) -> list[str]:
        packages = [
            "budgie-desktop",
            "budgie-desktop-view",
            "budgie-screensaver",
            "gnome-control-center",
            "gnome-terminal",
            "nautilus",
            "xorg-server",
            "alsa-utils",
            "pulseaudio",
            "pulseaudio-alsa",
            "pavucontrol",
            "arc-gtk-theme",
            "arc-icon-theme",
        ]
        if self.display_manager:
            packages.extend(
                ["lightdm", "lightdm-gtk-greeter", "lightdm-gtk-greeter-settings"]
            )
        return packages

    def prompt_extra(self):
        self.display_manager = archcraftsman.utils.prompt_bool(
            _("The display manager to install is '%s'. Do you want to install it ?")
            % "LightDM",
            default=True,
        )

    def print_resume(self):
        archcraftsman.base.print_sub_step(_("Desktop environment : %s") % self.name)
        archcraftsman.base.print_sub_step(
            _("Display manager : %s")
            % ("LightDM" if self.display_manager else _("none"))
        )

    def configure(self):
        if self.display_manager:
            archcraftsman.base.execute("systemctl enable lightdm", chroot=True)
        archcraftsman.info.ai.pre_launch_info.setup_chroot_keyboard()
