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
The module of PartitioningInfo class.
"""
import re
import subprocess

import archcraftsman.arguments
import archcraftsman.base
import archcraftsman.i18n
import archcraftsman.options
import archcraftsman.partition

_ = archcraftsman.i18n.translate


class PartitioningInfo:
    """
    The class to contain all partitioning information.
    """

    def __init__(self, swapfile_size: str = "", main_disk: str = "") -> None:
        self.partitions: list[archcraftsman.partition.Partition] = []
        self.swapfile_size = swapfile_size
        self.main_disk = main_disk
        self._btrfs_in_use = False
        self._xfs_in_use = False

    def root_partition(self) -> archcraftsman.partition.Partition:
        """
        The root partition retrieving method.
        """
        return next(
            partition
            for partition in self.partitions
            if partition.part_type == archcraftsman.options.PartTypes.ROOT
        )

    def format_and_mount_partitions(self):
        """
        A method to format and mount all partitions.
        """
        archcraftsman.base.print_step(
            _("Formatting and mounting partitions..."), clear=False
        )

        formatting_ok = False
        while not formatting_ok:
            try:
                for partition in self.partitions:
                    if (
                        partition.part_format_type
                        == archcraftsman.options.FSFormats.BTRFS
                    ):
                        self._btrfs_in_use = True
                    elif (
                        partition.part_format_type
                        == archcraftsman.options.FSFormats.XFS
                    ):
                        self._xfs_in_use = True
                    partition.format_partition()
                formatting_ok = True
            except subprocess.CalledProcessError as exception:
                self.umount_partitions()
                archcraftsman.base.print_error(
                    _("A subprocess execution failed ! See the following error: %s")
                    % exception
                )

        not_mounted_partitions = [
            partition
            for partition in self.partitions
            if not partition.is_mounted() and partition.part_mount_point
        ]
        not_mounted_partitions.sort(
            key=lambda part: 0
            if not part.part_mount_point
            else len(part.part_mount_point)
        )

        while not archcraftsman.arguments.test() and False in [
            partition.is_mounted() for partition in not_mounted_partitions
        ]:
            for partition in not_mounted_partitions:
                if partition.part_format_type == archcraftsman.options.FSFormats.BTRFS:
                    self._btrfs_in_use = True
                elif partition.part_format_type == archcraftsman.options.FSFormats.XFS:
                    self._xfs_in_use = True
                partition.mount()

    def umount_partitions(self):
        """
        A method to unmount all mounted partitions.
        """
        archcraftsman.base.print_step(_("Unmounting partitions..."), clear=False)
        swap = re.sub(
            "\\s",
            "",
            archcraftsman.base.execute(
                "swapon --noheadings | awk '{print $1}'",
                check=False,
                capture_output=True,
            ).output,
        )
        if swap:
            archcraftsman.base.execute(f"swapoff {swap} &>/dev/null", check=False)

        mounted_partitions = [
            partition for partition in self.partitions if partition.is_mounted()
        ]
        mounted_partitions.sort(
            key=lambda part: 0
            if not part.part_mount_point
            else len(part.part_mount_point),
            reverse=True,
        )

        while not archcraftsman.arguments.test() and True in [
            partition.is_mounted() for partition in mounted_partitions
        ]:
            for partition in [
                partition for partition in mounted_partitions if partition.is_mounted()
            ]:
                partition.umount()
