"""
The module of PartitioningInfo class.
"""
from src.i18n import I18n
from src.options import FSFormats
from src.partition import Partition
from src.utils import print_step

_ = I18n().gettext


class PartitioningInfo:
    """
    The class to contain all partitioning information.
    """
    partitions: list[Partition]
    root_partition: Partition
    swapfile_size: str
    main_disk: str

    btrfs_in_use: bool = False

    def __init__(self) -> None:
        self.partitions = []

    def format_and_mount_partitions(self):
        """
        A method to format and mount all partitions.
        :return:
        """
        print_step(_("Formatting and mounting partitions..."), clear=False)

        for partition in self.partitions:
            if partition.part_format_type == FSFormats.BTRFS:
                self.btrfs_in_use = True
            partition.format_partition()

        if self.root_partition.part_format_type == FSFormats.BTRFS:
            self.btrfs_in_use = True
        self.root_partition.mount()

        for partition in [partition for partition in self.partitions if not partition.part_mounted]:
            if partition.part_format_type == FSFormats.BTRFS:
                self.btrfs_in_use = True
            partition.mount()
