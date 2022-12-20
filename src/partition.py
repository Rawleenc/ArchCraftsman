import os
import re

from src.utils import from_iec


class Partition:
    """
    A class to represent a partition.
    """
    path: str
    size: int
    part_type: str
    fs_type: str

    def __init__(self, part_str: str = None):
        """
        Partition initialisation.
        """
        if part_str is None:
            self.path = ""
            self.size = 0
            self.part_type = ""
            self.fs_type = ""
        else:
            self.path = part_str.split(" ")[0]
            self.size = from_iec(re.sub('\\s', '', os.popen(f'lsblk -nl "{self.path}" -o SIZE').read()))
            self.part_type = str(
                re.sub('[^a-zA-Z\\d ]', '', os.popen(f'lsblk -nl "{self.path}" -o PARTTYPENAME').read()))
            self.fs_type = str(
                re.sub('[^a-zA-Z\\d ]', '', os.popen(f'lsblk -nl "{self.path}" -o FSTYPE').read()))

    def __str__(self) -> str:
        """
        Partition str formatting.
        """
        return f"'{self.path}' - '{self.size}' - '{self.part_type}' - '{self.fs_type}'"
