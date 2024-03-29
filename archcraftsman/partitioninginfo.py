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
import archcraftsman.disk
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

    def filesystem_in_use(self) -> archcraftsman.options.FSFormats:
        """
        A method to retrieve the main filesystem in use in this partitioning.
        Falls back to ext4 if no particular filesystem is in use.
        """
        if self._btrfs_in_use:
            return archcraftsman.options.FSFormats.BTRFS
        return archcraftsman.options.FSFormats.EXT4

    def root_partition(self) -> archcraftsman.partition.Partition:
        """
        The root partition retrieving method.
        """
        return next(
            partition
            for partition in self.partitions
            if partition.part_type == archcraftsman.options.PartTypes.ROOT
        )

    def efi_partition(self) -> archcraftsman.partition.Partition:
        """
        The Disk method to get the EFI partition if it exist. Else return an empty partition object.
        """
        return next(
            (
                partition
                for partition in self.partitions
                if partition.part_type == archcraftsman.options.PartTypes.EFI
            ),
            next(
                (
                    partition
                    for partition in self.partitions
                    if partition.part_type == archcraftsman.options.PartTypes.BOOT
                    and partition.part_format_type
                    == archcraftsman.options.FSFormats.VFAT
                ),
                archcraftsman.partition.Partition(
                    part_type=archcraftsman.options.PartTypes.EFI,
                    part_format_type=archcraftsman.options.FSFormats.VFAT,
                    part_mount_point="/boot/efi",
                ),
            ),
        )

    def format_and_mount_partitions(self):
        """
        A method to format and mount all partitions.
        """
        archcraftsman.base.print_step(
            _("Formatting and mounting partitions..."), clear=False
        )

        part_mount_points = [
            partition.part_mount_point
            for partition in self.partitions
            if partition.part_mount_point
        ]

        count = 0
        formatting_ok = False
        while not formatting_ok:
            try:
                for partition in self.partitions:
                    if (
                        partition.part_format_type
                        == archcraftsman.options.FSFormats.BTRFS
                    ):
                        self._btrfs_in_use = True
                    partition.formatting(part_mount_points)
                formatting_ok = True
            except subprocess.CalledProcessError as exception:
                self.umount_partitions()
                archcraftsman.base.print_error(
                    _("A subprocess execution failed ! See the following error: %s")
                    % exception
                )
                if count >= 5:
                    archcraftsman.base.print_error(
                        _("Too many subprocess execution failures, aborting...")
                    )
                    raise exception
                count += 1

        not_mounted_partitions = [
            partition
            for partition in self.partitions
            if not partition.is_mounted()
            and partition.part_type != archcraftsman.options.PartTypes.SWAP
            and partition.part_mount_point
        ]
        not_mounted_partitions.sort(
            key=lambda part: (
                0 if not part.part_mount_point else len(part.part_mount_point)
            )
        )

        count = 0
        while not archcraftsman.arguments.test() and False in [
            partition.is_mounted() for partition in not_mounted_partitions
        ]:
            for partition in not_mounted_partitions:
                if partition.part_format_type == archcraftsman.options.FSFormats.BTRFS:
                    self._btrfs_in_use = True
                partition.mount(part_mount_points)
            if count >= 5:
                archcraftsman.base.print_error(
                    _("Too many subprocess execution failures, aborting...")
                )
                raise subprocess.CalledProcessError(1, "mount")
            count += 1

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
            key=lambda part: (
                0 if not part.part_mount_point else len(part.part_mount_point)
            ),
            reverse=True,
        )

        count = 0
        while not archcraftsman.arguments.test() and True in [
            partition.is_mounted() for partition in mounted_partitions
        ]:
            for partition in [
                partition for partition in mounted_partitions if partition.is_mounted()
            ]:
                partition.umount()
            if count >= 5:
                archcraftsman.base.print_error(
                    _("Too many subprocess execution failures, aborting...")
                )
                raise subprocess.CalledProcessError(1, "umount")
            count += 1
