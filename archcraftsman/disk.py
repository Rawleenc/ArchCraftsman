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
The disk class module
"""
import re
from typing import Optional

from archcraftsman.i18n import I18n
from archcraftsman.options import PartTypes
from archcraftsman.partition import Partition
from archcraftsman.utils import to_iec, prompt, print_error, execute

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
        detected_partitions = execute(
            f'lsblk -nl "{path}" -o PATH,TYPE,PARTTYPENAME | grep part | grep -iE "linux|efi|swap"',
            force=True,
            check=False,
            capture_output=True,
        ).output
        self.partitions = []
        index = 0
        for partition_info in detected_partitions.splitlines():
            self.partitions.append(Partition(index, partition_info.split(" ")[0]))
            index += 1
        self.total = int(
            execute(
                f'lsblk -b --output SIZE -n -d "{self.path}"',
                force=True,
                capture_output=True,
            ).output
        )
        if len(self.partitions) > 0:
            sector_size = int(
                re.sub(
                    "\\s",
                    "",
                    execute(
                        f"lsblk {path} -o PATH,TYPE,PHY-SEC | grep disk | awk '{{print $3}}'",
                        force=True,
                        capture_output=True,
                    ).output,
                )
            )
            last_partition_path = [p.path for p in self.partitions][
                len(self.partitions) - 1
            ]
            last_sector = int(
                re.sub(
                    "\\s",
                    "",
                    execute(
                        f"fdisk -l | grep {last_partition_path} | awk '{{print $3}}'",
                        force=True,
                        capture_output=True,
                    ).output,
                )
            )
            self.free_space = self.total - (last_sector * sector_size)
        else:
            self.free_space = self.total

    def get_efi_partition(self) -> Partition:
        """
        The Disk method to get the EFI partition if it exist. Else return an empty partition object.
        """
        try:
            return [
                p for p in self.partitions if PartTypes.EFI in p.part_type_name
            ].pop()
        except IndexError:
            return Partition(None)

    def ask_swapfile_size(self) -> Optional[str]:
        """
        The method to ask the user for the swapfile size.
        """
        swapfile_ok = False
        swapfile_size = ""
        swapfile_size_pattern = re.compile("^(\\d*[.,]\\d+|\\d+)([GMk])$")
        default_swapfile_size = to_iec(int(self.total / 32))
        while not swapfile_ok:
            swapfile_size = prompt(
                _("Swapfile size ? (%s, type '0' for none) : ") % default_swapfile_size,
                default=default_swapfile_size,
            )
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
