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

from archcraftsman.bundles.bundle import Bundle
from archcraftsman.globalinfo import GlobalInfo
from archcraftsman.i18n import I18n
from archcraftsman.utils import print_sub_step, prompt_bool, execute

_ = I18n().gettext


class Budgie(Bundle):
    """
    Bundle class.
    """

    display_manager = True

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
        self.display_manager = prompt_bool(
            _("The display manager to install is '%s'. Do you want to install it ?")
            % "LightDM",
            default=True,
        )

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(
            _("Display manager : %s")
            % ("LightDM" if self.display_manager else _("none"))
        )

    def configure(self):
        if self.display_manager:
            execute('arch-chroot /mnt bash -c "systemctl enable lightdm"')
        GlobalInfo().pre_launch_info.setup_chroot_keyboard()
