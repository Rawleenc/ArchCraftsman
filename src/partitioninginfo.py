"""
The module of PartitioningInfo class.
"""
import re
from typing import Optional

from src.i18n import I18n
from src.options import FSFormats
from src.partition import Partition
from src.utils import print_step, execute

_ = I18n().gettext


class PartitioningInfo:
    """
    The class to contain all partitioning information.
    """

    partitions: list[Partition]
    root_partition: Partition
    swapfile_size: Optional[str]
    main_disk: str

    btrfs_in_use: bool = False

    def __init__(self) -> None:
        self.partitions = []

    def format_and_mount_partitions(self):
        """
        A method to format and mount all partitions.
        """
        print_step(_("Formatting and mounting partitions..."), clear=False)

        for partition in self.partitions:
            if partition.part_format_type == FSFormats.BTRFS:
                self.btrfs_in_use = True
            partition.format_partition()

        not_mounted_partitions = [
            partition
            for partition in self.partitions
            if not partition.part_mounted and partition.part_mount_point
        ]
        not_mounted_partitions.sort(
            key=lambda part: 0
            if not part.part_mount_point
            else len(part.part_mount_point)
        )

        while False in [partition.part_mounted for partition in not_mounted_partitions]:
            for partition in not_mounted_partitions:
                if partition.part_format_type == FSFormats.BTRFS:
                    self.btrfs_in_use = True
                partition.mount()

        for partition in self.partitions:
            partition.compute()

    def umount_partitions(self):
        """
        A method to unmount all mounted partitions.
        """
        print_step(_("Unmounting partitions..."), clear=False)
        swap = re.sub(
            "\\s",
            "",
            execute(
                "swapon --noheadings | awk '{print $1}'",
                check=False,
                capture_output=True,
            ).output,
        )
        if swap:
            execute(f"swapoff {swap} &>/dev/null", check=False)

        mounted_partitions = [
            partition for partition in self.partitions if partition.part_mounted
        ]
        mounted_partitions.sort(
            key=lambda part: 0
            if not part.part_mount_point
            else len(part.part_mount_point),
            reverse=True,
        )

        while True in [partition.part_mounted for partition in mounted_partitions]:
            for partition in [
                partition for partition in mounted_partitions if partition.part_mounted
            ]:
                partition.umount()
