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

from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import I18n
from archcraftsman.partitioninginfo import PartitioningInfo
from archcraftsman.prelaunchinfo import PreLaunchInfo
from archcraftsman.systeminfo import SystemInfo
from archcraftsman.utils import print_sub_step, prompt_bool, execute

_ = I18n().gettext


class Gnome(Bundle):
    """
    Bundle class.
    """

    minimal = False

    def packages(self, system_info: SystemInfo) -> list[str]:
        packages = [
            "gnome",
            "alsa-utils",
            "pulseaudio",
            "pulseaudio-alsa",
            "xdg-desktop-portal",
            "xdg-desktop-portal-gnome",
            "qt5-wayland",
        ]
        if self.minimal is not True:
            packages.append("gnome-extra")
        return packages

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % "GDM")

    def prompt_extra(self):
        self.minimal = prompt_bool(
            _("Install a minimal environment ?"),
            default=False,
            help_msg=_(
                "If yes, the script will not install any extra packages, only base packages."
            ),
        )

    def configure(
        self,
        system_info: SystemInfo,
        pre_launch_info: PreLaunchInfo,
        partitioning_info: PartitioningInfo,
    ):
        execute('arch-chroot /mnt bash -c "systemctl enable gdm"')
        pre_launch_info.setup_chroot_keyboard()