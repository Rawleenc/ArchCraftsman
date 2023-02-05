"""
The module of PartitioningInfo class.
"""
from src.partition import Partition


class PartitioningInfo:
    """
    The class to contain all partitioning information.
    """
    partitions: [Partition]
    root_partition: Partition
    swapfile_size: str
    main_disk: str

    def __init__(self) -> None:
        self.partitions = []
