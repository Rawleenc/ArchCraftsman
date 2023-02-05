"""
The disk class module
"""
import re

from src.i18n import I18n
from src.options import PartTypes
from src.partition import Partition
from src.utils import to_iec, prompt, print_error, execute, stdout

_ = I18n().gettext


class Disk:
    """
    A class to represent a disk.
    """
    path: str
    partitions: list
    total: int
    free_space: int

    def __init__(self, path: str):
        """
        Disk initialisation.
        """
        self.path = path
        detected_partitions = stdout(execute(f'lsblk -nl "{path}" -o PATH,TYPE | grep part', capture_output=True,
                                             force=True, check=False))
        self.partitions = []
        index = 0
        for partition_info in detected_partitions.splitlines():
            self.partitions.append(Partition(index, partition_info.split(" ")[0]))
            index += 1
        self.total = int(
            stdout(execute(f'lsblk -b --output SIZE -n -d "{self.path}"', capture_output=True, force=True)))
        if len(self.partitions) > 0:
            sector_size = int(
                re.sub('\\s', '',
                       stdout(execute(f'lsblk {path} -o PATH,TYPE,PHY-SEC | grep disk | awk \'{{print $3}}\'',
                                      capture_output=True, force=True))))
            last_partition_path = [p.path for p in self.partitions][len(self.partitions) - 1]
            last_sector = int(
                re.sub('\\s', '', stdout(execute(f'fdisk -l | grep {last_partition_path} | awk \'{{print $3}}\'',
                                                 capture_output=True, force=True))))
            self.free_space = self.total - (last_sector * sector_size)
        else:
            self.free_space = self.total

    def get_efi_partition(self) -> Partition:
        """
        The Disk method to get the EFI partition if it exist. Else return an empty partition object.
        """
        try:
            return [p for p in self.partitions if PartTypes.EFI in p.part_type_name].pop()
        except IndexError:
            return Partition(None)

    def ask_swapfile_size(self) -> str:
        """
        The method to ask the user for the swapfile size.
        :return:
        """
        swapfile_ok = False
        swapfile_size = ""
        swapfile_size_pattern = re.compile("^(\\d*[.,]\\d+|\\d+)([GMk])$")
        default_swapfile_size = to_iec(int(self.total / 32))
        while not swapfile_ok:
            swapfile_size = prompt(_("Swapfile size ? (%s, type '0' for none) : ") % default_swapfile_size,
                                   default=default_swapfile_size)
            if swapfile_size == "0":
                swapfile_size = None
                swapfile_ok = True
            elif swapfile_size_pattern.match(swapfile_size):
                swapfile_ok = True
            else:
                print_error("Invalid swapfile size.")
        return swapfile_size

    def __str__(self) -> str:
        """
        Disk str formatting
        """
        return "\n".join([str(p) for p in self.partitions])
