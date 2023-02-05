"""
The partition class module
"""
import json
import os
import re

from src.i18n import I18n
from src.options import PartTypes, FSFormats
from src.utils import from_iec, execute, stdout, prompt_bool, prompt_ln, ask_password, print_error, to_iec

_ = I18n().gettext


class Partition:
    """
    A class to represent a partition.
    """
    index: int
    path: str
    size: int
    part_type_name: str
    fs_type: str
    part_type: PartTypes
    part_mount_point: str
    part_format_type: FSFormats
    part_format: bool

    encrypted: bool = False
    block_name: str = None
    block_password: str = None

    def __init__(self, index: int or None = None, path: str = None, part_type: PartTypes = None,
                 part_mount_point: str = None,
                 part_format_type: FSFormats = None, part_format: bool = True, compute: bool = True):
        """
        Partition initialisation.
        """
        self.index = index
        self.part_type = part_type
        self.part_mount_point = part_mount_point
        self.part_format_type = part_format_type
        self.part_format = part_format
        if path is None:
            self.path = ""
            self.size = 0
            self.part_type_name = ""
            self.fs_type = ""
        else:
            self.path = path
            if compute:
                self.compute()

    def __str__(self) -> str:
        """
        Partition str formatting.
        """
        formatted_str = f"'{self.path}' - '{self.part_type_name}' - '{to_iec(int(self.size))}'"
        if self.encrypted:
            formatted_str += f" - encrypted ('/dev/mapper/{self.block_name}')"
        return formatted_str

    def compute(self):
        """
        A method to compute partition information.
        :return:
        """
        self.size = from_iec(re.sub('\\s', '', stdout(
            execute(f'lsblk -nl "{self.path}" -o SIZE', capture_output=True, force=True))))
        self.part_type_name = str(re.sub('[^a-zA-Z\\d ]', '', stdout(
            execute(f'lsblk -nl "{self.path}" -o PARTTYPENAME', capture_output=True, force=True))))
        self.fs_type = str(re.sub('[^a-zA-Z\\d ]', '', stdout(
            execute(f'lsblk -nl "{self.path}" -o FSTYPE', capture_output=True, force=True))))

    def ask_for_encryption(self):
        """
        A method to ask if the partition will be encrypted.
        :return:
        """
        self.encrypted = prompt_bool(_("Do you want to encrypt this partition ? (y/N) : "), default=False)
        if self.encrypted:

            block_name_pattern = re.compile("^[a-z][a-z\\d_]*$")
            block_name_ok = False
            while not block_name_ok:
                self.block_name = prompt_ln(_("What will be the encrypted block name ? : "), required=True)
                if self.block_name and self.block_name != "" and not block_name_pattern.match(
                        self.block_name):
                    print_error(_("Invalid encrypted block name."))
                    continue
                block_name_ok = True

            self.block_password = ask_password(
                _("Enter the encrypted block password (it will be asked at boot to decrypt the partition) : "),
                required=True)

    def summary(self):
        """
        A method to get the partition summary.
        :return:
        """
        if self.part_format:
            formatting = _("yes")
        else:
            formatting = _("no")
        name = "NO_NAME"
        if self.index:
            name = str(self.index + 1)
        if self.path:
            name = self.path
        if self.part_type == PartTypes.SWAP:
            return _("%s : %s") % (self.part_type, name)
        return _("%s : %s (mounting point : %s, format %s, format type %s)") % (
            self.part_type, name, self.part_mount_point, formatting, self.part_format_type)

    def format_partition(self):
        """
        A method to execute formatting commands for the partition.
        """
        if self.part_type == PartTypes.SWAP:
            execute(f'mkswap "{self.path}"')
            execute(f'swapon "{self.path}"')
            return
        match self.part_format_type:
            case FSFormats.VFAT:
                if self.part_format:
                    execute(f'mkfs.vfat "{self.path}"')
                execute(f'mkdir -p "/mnt{self.part_mount_point}"')
                execute(f'mount "{self.path}" "/mnt{self.part_mount_point}"')
            case FSFormats.BTRFS:
                if self.part_format:
                    execute(f'mkfs.btrfs -f "{self.path}"')
                execute(f'mkdir -p "/mnt{self.part_mount_point}"')
                execute(f'mount -o compress=zstd "{self.path}" "/mnt{self.part_mount_point}"')
            case _:
                if self.part_format:
                    execute(f'mkfs.ext4 "{self.path}"')
                execute(f'mkdir -p "/mnt{self.part_mount_point}"')
                execute(f'mount "{self.path}" "/mnt{self.part_mount_point}"')

    def build_partition_name(self, disk_name: str):
        """
        A method to build a partition name with a disk and an index.
        :param disk_name:
        :return:
        """
        block_devices_str = stdout(execute('lsblk -J', capture_output=True, force=True))
        if not block_devices_str:
            return
        block_devices_json = json.loads(block_devices_str)
        if block_devices_json is None or not isinstance(block_devices_json, dict) or "blockdevices" not in dict(
                block_devices_json):
            return
        block_devices = dict(block_devices_json).get("blockdevices")
        if block_devices is None or not isinstance(block_devices, list):
            return
        disk = next((d for d in block_devices if
                     d is not None and isinstance(d, dict) and "name" in d and dict(d).get("name") == os.path.basename(
                         disk_name)), None)
        if disk is None or not isinstance(disk, dict) or "children" not in dict(disk):
            return
        partitions = dict(disk).get("children")
        if partitions is None or not isinstance(partitions, list) or len(list(partitions)) <= self.index:
            return
        partition = list(partitions)[self.index]
        if partition is None or not isinstance(partition, dict) or "name" not in dict(partition):
            return
        self.path = f'/dev/{dict(partition).get("name")}'
