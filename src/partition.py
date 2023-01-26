"""
The partition class module
"""
import re

from src.i18n import I18n
from src.utils import from_iec, execute, stdout, prompt_bool, prompt_ln, ask_password, print_error

_ = I18n().gettext


class Partition:
    """
    A class to represent a partition.
    """
    index: int
    path: str
    size: int
    part_type: str
    fs_type: str
    encrypted: bool = False
    block_name: str = None
    block_password: str = None

    def __init__(self, index: int or None, path: str = None, compute: bool = True):
        """
        Partition initialisation.
        """
        self.index = index
        if path is None:
            self.path = ""
            self.size = 0
            self.part_type = ""
            self.fs_type = ""
        else:
            self.path = path
            if compute:
                self.compute()

    def compute(self):
        self.size = from_iec(re.sub('\\s', '', stdout(
            execute(f'lsblk -nl "{self.path}" -o SIZE', capture_output=True, force=True))))
        self.part_type = str(re.sub('[^a-zA-Z\\d ]', '', stdout(
            execute(f'lsblk -nl "{self.path}" -o PARTTYPENAME', capture_output=True, force=True))))
        self.fs_type = str(re.sub('[^a-zA-Z\\d ]', '', stdout(
            execute(f'lsblk -nl "{self.path}" -o FSTYPE', capture_output=True, force=True))))

    def ask_for_encryption(self):
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

    def __str__(self) -> str:
        """
        Partition str formatting.
        """
        formatted_str = f"'{self.path}' - '{self.size}' - '{self.part_type}' - '{self.fs_type}'"
        if self.encrypted:
            formatted_str += f" - encrypted ('/dev/mapper/{self.block_name}')"
        return formatted_str
