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
The zram bundle module
"""
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import I18n
from archcraftsman.partitioninginfo import PartitioningInfo
from archcraftsman.prelaunchinfo import PreLaunchInfo
from archcraftsman.systeminfo import SystemInfo
from archcraftsman.utils import print_sub_step, log

_ = I18n().gettext


class Zram(Bundle):
    """
    The ZRAM class.
    """

    def packages(self, system_info: SystemInfo) -> list[str]:
        return ["zram-generator"]

    def print_resume(self):
        print_sub_step(_("Install and enable ZRAM."))

    def configure(
        self,
        system_info: SystemInfo,
        pre_launch_info: PreLaunchInfo,
        partitioning_info: PartitioningInfo,
    ):
        content = ["[zram0]\n", "zram-size = ram / 2\n"]
        try:
            with open(
                "/mnt/etc/systemd/zram-generator.conf", "w", encoding="UTF-8"
            ) as zram_config_file:
                zram_config_file.writelines(content)
        except FileNotFoundError as exception:
            log(f"Exception: {exception}")
