"""
The partition class module
"""
import re

from src.utils import from_iec, execute, stdout


class Partition:
    """
    A class to represent a partition.
    """
    index: int
    path: str
    size: int
    part_type: str
    fs_type: str

    def __init__(self, index: int or None, part_str: str = None):
        """
        Partition initialisation.
        """
        self.index = index
        if part_str is None:
            self.path = ""
            self.size = 0
            self.part_type = ""
            self.fs_type = ""
        else:
            self.path = part_str.split(" ")[0]
            self.size = from_iec(
                re.sub('\\s', '', stdout(execute(f'lsblk -nl "{self.path}" -o SIZE', capture_output=True, force=True))))
            self.part_type = str(
                re.sub('[^a-zA-Z\\d ]', '',
                       stdout(execute(f'lsblk -nl "{self.path}" -o PARTTYPENAME', capture_output=True, force=True))))
            self.fs_type = str(
                re.sub('[^a-zA-Z\\d ]', '',
                       stdout(execute(f'lsblk -nl "{self.path}" -o FSTYPE', capture_output=True, force=True))))

    def __str__(self) -> str:
        """
        Partition str formatting.
        """
        return f"'{self.path}' - '{self.size}' - '{self.part_type}' - '{self.fs_type}'"
