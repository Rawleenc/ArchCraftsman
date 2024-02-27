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
The copy ArchCraftsman bundle module
"""
import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.i18n
import archcraftsman.info
import archcraftsman.options

_ = archcraftsman.i18n.translate


class CopyACM(archcraftsman.bundles.bundle.Bundle):
    """
    The CopyACM class.
    """

    def __init__(self):
        super().__init__(archcraftsman.options.Bundles.ARCHITECT)

    def prompt(self) -> str:
        return _("Execute GLF's Architect post-installation script ?")

    def print_resume(self):
        archcraftsman.base.print_sub_step(
            _("Execute GLF's Architect post-installation script.")
        )

    def configure(self):
        if archcraftsman.info.ai.system_info.user_name:
            path = f"/home/{archcraftsman.info.ai.system_info.user_name}"
            archcraftsman.base.execute(
                f"git clone https://github.com/Gaming-Linux-FR/Architect.git {path}/Architect",
                chroot=True,
                user=archcraftsman.info.ai.system_info.user_name,
            )
            archcraftsman.base.execute(
                "cd ~/Architect && chmod +x architect.sh && ./architect.sh --no-reboot",
                chroot=True,
                user=archcraftsman.info.ai.system_info.user_name,
                interactive=True,
                check=False,
            )
        else:
            archcraftsman.base.print_warning(
                _("No user found. Architect execution avoided."), do_pause=False
            )
