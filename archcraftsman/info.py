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
The config related methods module
"""


import archcraftsman.partitioninginfo
import archcraftsman.prelaunchinfo
import archcraftsman.systeminfo


class AllInfo:
    """
    The singleton implementation containing the translation method to use.
    """

    def __init__(self) -> None:
        self.pre_launch_info: archcraftsman.prelaunchinfo.PreLaunchInfo = (
            archcraftsman.prelaunchinfo.PreLaunchInfo()
        )
        self.partitioning_info: archcraftsman.partitioninginfo.PartitioningInfo = (
            archcraftsman.partitioninginfo.PartitioningInfo()
        )
        self.system_info: archcraftsman.systeminfo.SystemInfo = (
            archcraftsman.systeminfo.SystemInfo()
        )


ai = AllInfo()
