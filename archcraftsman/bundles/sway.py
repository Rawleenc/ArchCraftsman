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
The sway bundle module
"""

import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.i18n
import archcraftsman.info
import archcraftsman.options

_ = archcraftsman.i18n.translate


class Sway(archcraftsman.bundles.bundle.Bundle):
    """
    Bundle class.
    """

    def __init__(self):
        super().__init__(archcraftsman.options.Desktops.SWAY)

    def packages(self) -> list[str]:
        packages = [
            "sway",
            "dmenu",
            "bemenu-wayland",
            "j4-dmenu-desktop",
            "foot",
            "grim",
            "mako",
            "slurp",
            "swayidle",
            "swaylock",
            "swayimg",
            "waybar",
            "swaybg",
            "wf-recorder",
            "wl-clipboard",
            "xorg-xwayland",
            "alsa-utils",
            "pulseaudio",
            "pulseaudio-alsa",
            "pavucontrol",
            "system-config-printer",
            "acpid",
            "brightnessctl",
            "playerctl",
            "gammastep",
            "dex",
            "libindicator-gtk2",
            "libindicator-gtk3",
            "gnome-keyring",
            "xdg-desktop-portal",
            "xdg-desktop-portal-wlr",
        ]
        return packages

    def print_resume(self):
        archcraftsman.base.print_sub_step(_("Desktop environment : %s") % self.name)
        archcraftsman.base.print_sub_step(_("Display manager : %s") % _("none"))

    def configure(self):
        archcraftsman.base.execute("systemctl enable acpid", chroot=True)
        archcraftsman.info.ai.pre_launch_info.setup_chroot_keyboard()
        if "fr" in archcraftsman.info.ai.pre_launch_info.keymap:
            archcraftsman.base.execute(
                "echo 'XKB_DEFAULT_LAYOUT=fr' >> /mnt/etc/environment"
            )
