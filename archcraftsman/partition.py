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
The partition class module
"""
import json
import os
from subprocess import CalledProcessError
from typing import Optional

from archcraftsman.base import execute, print_sub_step, prompt_bool
from archcraftsman.i18n import _
from archcraftsman.options import FSFormats, PartTypes
from archcraftsman.utils import (
    ask_encryption_block_name,
    ask_format_type,
    from_iec,
    to_iec,
)


class Partition:
    """
    A class to represent a partition.
    """

    def __init__(
        self,
        index: int = 0,
        path: str = "",
        part_type: PartTypes = PartTypes.OTHER,
        part_mount_point: str = "",
        part_format_type: FSFormats = FSFormats.EXT4,
        part_format: bool = True,
        encrypted: bool = False,
        block_name: str = "",
    ):
        """
        Partition initialisation.
        """
        self.index = index
        self.part_type = part_type
        self.part_mount_point = part_mount_point
        self.part_format_type = part_format_type
        self.part_format = part_format
        self.encrypted = encrypted
        self.block_name = block_name
        self.path = path

    def __str__(self) -> str:
        """
        Partition str formatting.
        """
        formatted_str = (
            f"'{self.path}' - '{self.part_type_name()}' - '{to_iec(int(self.size()))}'"
        )
        return formatted_str

    def size(self) -> int:
        """
        A method to get the partition size.
        """
        return from_iec(
            execute(
                f'lsblk -nld "{self.path}" -o SIZE', force=True, capture_output=True
            ).output.strip()
        )

    def part_type_name(self) -> str:
        """
        A method to get the partition type name.
        """
        return execute(
            f'lsblk -nld "{self.path}" -o PARTTYPENAME',
            force=True,
            capture_output=True,
        ).output.strip()

    def disk_name(self) -> str:
        """
        A method to get the disk name.
        """
        return execute(
            f'lsblk -nld "{self.path}" -o PKNAME', force=True, capture_output=True
        ).output.strip()

    def fs_type(self) -> str:
        """
        A method to get the filesystem type.
        """
        return execute(
            f'lsblk -nld "{self.path}" -o FSTYPE', force=True, capture_output=True
        ).output.strip()

    def uuid(self) -> str:
        """
        A method to get the partition uuid.
        """
        return execute(
            f'lsblk -nld "{self.path}" -o UUID', force=True, capture_output=True
        ).output.strip()

    def need_format(self):
        """
        Method to know if the partition need to be formatted
        """
        return self.part_type in {PartTypes.ROOT}

    def no_format(self):
        """
        Method to know if the partition doesn't have to be formatted
        """
        return self.part_type in {PartTypes.SWAP, PartTypes.NOT_USED}

    def ask_for_format(self):
        """
        Method to ask if the partition have to be formatted and in which format.
        """
        if self.no_format():
            self.part_format = False
            return
        if self.need_format() or self.encrypted:
            self.part_format = True
            self.part_format_type = ask_format_type()
            return
        self.part_format = prompt_bool(_("Format the partition ?"))
        if self.part_format:
            if self.part_type == PartTypes.EFI:
                self.part_format_type = FSFormats.VFAT
            else:
                self.part_format_type = ask_format_type()

    def is_encrypted(self) -> bool:
        """
        A method to detect if the partition is an existing-encrypted partition.
        """
        return bool(
            execute(
                f"cryptsetup isLuks {self.path}", check=False, force=True, sudo=True
            )
        )

    def is_encryptable(self):
        """
        Method to know if the partition is encryptable.
        """
        return self.part_type in {PartTypes.ROOT, PartTypes.HOME, PartTypes.OTHER}

    def ask_for_encryption(self):
        """
        A method to ask if the partition will be encrypted.
        """
        if not self.part_format:
            self.encrypted = self.is_encrypted()
        elif not self.is_encryptable():
            return
        else:
            self.encrypted = prompt_bool(
                _("Do you want to encrypt this partition ?"), default=False
            )
        if self.encrypted:
            if self.part_type == PartTypes.ROOT:
                self.block_name = "root"
            elif self.part_type == PartTypes.HOME:
                self.block_name = "home"
            else:
                self.block_name = ask_encryption_block_name()

    def summary(self):
        """
        A method to get the partition summary.
        """
        if self.part_format:
            formatting = _("yes")
        else:
            formatting = _("no")
        name = str(self.index + 1)
        if self.path:
            name = self.path
        if self.part_type == PartTypes.SWAP:
            return _("%s : %s") % (self.part_type, name)
        summary = _("%s : %s (mounting point : %s, format %s, format type %s)") % (
            self.part_type,
            name,
            self.part_mount_point,
            formatting,
            self.part_format_type,
        )
        if self.encrypted:
            summary += f" - {_('encrypted')} ('/dev/mapper/{self.block_name}')"
        return summary

    def real_path(self) -> Optional[str]:
        """
        A method to get the partition path.
        """
        return f"/dev/mapper/{self.block_name}" if self.encrypted else self.path

    def format_partition(self):
        """
        A method to execute formatting commands for the partition.
        """
        if self.part_format:
            print_sub_step(_("Formatting %s...") % (self.real_path()))
        if self.part_type == PartTypes.SWAP:
            execute(f'mkswap "{self.path}"')
            execute(f'swapon "{self.path}"')
            return
        if self.encrypted:
            if self.part_format:
                execute(f"cryptsetup -y -v luksFormat {self.path}")
            print_sub_step(_("Opening %s...") % (self.real_path()))
            execute(f"cryptsetup open {self.path} {self.block_name}")
        match self.part_format_type:
            case FSFormats.VFAT:
                if self.part_format:
                    execute(f'mkfs.vfat "{self.real_path()}"')
            case FSFormats.BTRFS:
                if self.part_format:
                    execute(f'mkfs.btrfs -f "{self.real_path()}"')
            case _:
                if self.part_format:
                    execute(f'mkfs.ext4 "{self.real_path()}"')

    def is_mounted(self) -> bool:
        """
        A method to detect if the partition is mounted.
        """
        return bool(
            execute(
                f"cat /proc/mounts | grep {self.real_path()}",
                check=False,
                capture_output=True,
                force=True,
            )
        )

    def mount(self):
        """
        A method to mount the partition.
        """
        print_sub_step(_("Mounting %s...") % (self.real_path()))
        match self.part_format_type:
            case FSFormats.BTRFS:
                execute(
                    f'mount --mkdir -o compress=zstd "{self.real_path()}" "/mnt{self.part_mount_point}"'
                )
            case _:
                execute(
                    f'mount --mkdir "{self.real_path()}" "/mnt{self.part_mount_point}"'
                )

    def umount(self) -> bool:
        """
        A method to unmount the partition.
        """
        try:
            print_sub_step(_("Unmounting %s...") % (self.real_path()))
            execute(f'umount "/mnt{self.part_mount_point}"')
            if self.encrypted:
                print_sub_step(_("Closing %s...") % (self.real_path()))
                execute(f"cryptsetup close {self.block_name}")
        except CalledProcessError:
            return False
        return True

    def build_partition_name(self, disk_name: str):
        """
        A method to build a partition name with a disk and an index.
        """
        block_devices_str = execute("lsblk -J", force=True, capture_output=True).output
        if not block_devices_str:
            return
        block_devices_json = json.loads(block_devices_str)
        if (
            not block_devices_json
            or not isinstance(block_devices_json, dict)
            or "blockdevices" not in dict(block_devices_json)
        ):
            return
        block_devices = dict(block_devices_json).get("blockdevices")
        if not block_devices or not isinstance(block_devices, list):
            return
        disk = next(
            (
                d
                for d in block_devices
                if d
                and isinstance(d, dict)
                and "name" in d
                and dict(d).get("name") == os.path.basename(disk_name)
            ),
            None,
        )
        if not disk or not isinstance(disk, dict) or "children" not in dict(disk):
            return
        partitions = dict(disk).get("children")
        if (
            not partitions
            or not isinstance(partitions, list)
            and len(list(partitions)) <= self.index
        ):
            return
        partition = list(partitions)[self.index]
        if (
            not partition
            or not isinstance(partition, dict)
            or "name" not in dict(partition)
        ):
            return
        self.path = f'/dev/{dict(partition).get("name")}'
