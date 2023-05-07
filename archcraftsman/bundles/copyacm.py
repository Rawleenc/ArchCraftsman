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
from archcraftsman import info
from archcraftsman.base import execute, print_sub_step
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import _
from archcraftsman.options import Bundles


class CopyACM(Bundle):
    """
    The CopyACM class.
    """

    def __init__(self):
        super().__init__(Bundles.COPY_ACM)

    def print_resume(self):
        print_sub_step(_("Copy ArchCraftsman to the new system."))

    def configure(self):
        if info.ai.system_info.user_name:
            path = f"/home/{info.ai.system_info.user_name}"
            execute(f"mkdir -p /mnt{path}")
            execute(f"cp -r ~/archcraftsman /mnt{path}")
            execute(
                (
                    f'arch-chroot /mnt bash -c "chown -R {info.ai.system_info.user_name}:'
                    f'{info.ai.system_info.user_name} {path}"'
                )
            )
        else:
            path = "/root"
            execute(f"mkdir -p /mnt{path}")
            execute(f"cp -r ~/archcraftsman /mnt{path}")
