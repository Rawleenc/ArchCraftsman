"""
LICENSE
archlinux-install, a very quick Arch Linux base installation script.
Copyright (C) 2021  Rawleenc

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

DISCLAIMER
archlinux-install  Copyright (C) 2021  Rawleenc

This program comes with ABSOLUTELY NO WARRANTY; See the
GNU General Public License for more details.

This is free software, and you are welcome to redistribute it
under certain conditions; See the GNU General Public License for more details.
"""
import getpass
import gettext
import glob
import json
import os
import re
import readline
import subprocess
import urllib.request

RED = "\033[0;31m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
ORANGE = "\033[0;33m"
NOCOLOR = "\033[0m"


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


class Disk:
    """
    A partition to represent a disk.
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
        detected_partitions = os.popen(f'lsblk -nl "{path}" -o PATH,TYPE | grep part').read()
        self.partitions = []
        for partition_info in detected_partitions.splitlines():
            self.partitions.append(Partition(partition_info))
        self.total = int(os.popen(f'lsblk -b --output SIZE -n -d "{self.path}"').read())
        if len(self.partitions) > 0:
            sector_size = int(
                re.sub('\\s', '',
                       os.popen(f'lsblk {path} -o PATH,TYPE,PHY-SEC | grep disk | awk \'{{print $3}}\'').read()))
            last_partition_path = [p.path for p in self.partitions][len(self.partitions) - 1]
            last_sector = int(
                re.sub('\\s', '', os.popen(f'fdisk -l | grep {last_partition_path} | awk \'{{print $3}}\'').read()))
            self.free_space = self.total - (last_sector * sector_size)
        else:
            self.free_space = self.total

    def get_efi_partition(self) -> Partition:
        """
        The Disk method to get the EFI partition if it exist. Else return an empty partition object.
        """
        try:
            return [p for p in self.partitions if "EFI" in p.part_type].pop()
        except IndexError:
            return Partition()

    def __str__(self) -> str:
        """
        Disk str formatting
        """
        return "\n".join([str(p) for p in self.partitions])


def complete(text, state):
    """
    A file path completer.
    :param text:
    :param state:
    :return:
    """
    return (glob.glob(text + '*') + [None])[state]


readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)


def print_error(message: str, do_pause: bool = True):
    """
    A method to print an error.
    :param message:
    :param do_pause:
    :return:
    """
    print(f'\n{RED}  /!\\ {message}{NOCOLOR}\n')
    if do_pause:
        pause(end_newline=True)


def print_step(message: str, clear: bool = True):
    """
    A method to print a step message.
    :param message:
    :param clear:
    """
    if clear:
        os.system('clear')
    print(f'\n{GREEN}{message}{NOCOLOR}')


def print_sub_step(message: str):
    """
    A method to print a sub step message.
    :param message:
    """
    print(f'{CYAN}  * {message}{NOCOLOR}')


def print_help(message: str, do_pause: bool = False):
    """
    A method to print an help message.
    :param message:
    :param do_pause:
    :return:
    """
    print_step(_("Help :"), clear=False)
    print_sub_step(message)
    if do_pause:
        pause(end_newline=True)


def prompt(message: str, default: str = None, help_msg: str = None) -> str:
    """
    A method to prompt for a user input.
    :param message:
    :param default:
    :param help_msg:
    :return:
    """
    user_input_ok = False
    user_input = None
    while not user_input_ok:
        user_input = input(f'{ORANGE}{message}{NOCOLOR}')
        if user_input == "?" and help_msg is not None and help_msg != "":
            print_help(help_msg)
            continue
        elif user_input == "" and default is not None:
            user_input = default
        user_input_ok = True
    return user_input


def prompt_ln(message: str, default: str = None, help_msg: str = None) -> str:
    """
    A method to prompt for a user input with a new line for the user input.
    :param message:
    :param default:
    :param help_msg:
    :return:
    """
    return prompt(f'{message}\n', default=default, help_msg=help_msg)


def prompt_bool(message: str, default: bool = True, help_msg: str = None) -> bool:
    """
    A method to prompt for a boolean choice.
    :param message:
    :param default:
    :param help_msg:
    :return:
    """
    if not default:
        return prompt(f'{message}', help_msg=help_msg).upper() in {"Y", "O"}
    return prompt(f'{message}', help_msg=help_msg).upper() != "N"


def prompt_passwd(message: str):
    """
    A method to prompt for a password without displaying an echo.
    :param message:
    :return:
    """
    return getpass.getpass(prompt=f'{ORANGE}{message}{NOCOLOR}')


def pause(start_newline: bool = False, end_newline: bool = False):
    """
    A method to insert a one key press pause.
    :param start_newline:
    :param end_newline:
    """
    message = _("Press any key to continue...")
    if start_newline:
        print("")
    print(f'{ORANGE}{message}{NOCOLOR}')
    os.system('read -n 1 -sr')
    if end_newline:
        print("")


def locale_setup(keymap: str = "de-latin1", global_language: str = "EN") -> str:
    """
    The method to setup environment locale.
    :param keymap:
    :param global_language:
    :return: The configured live system console font (terminus 16 or 32)
    """
    print_step(_("Configuring live environment..."), clear=False)
    os.system(f'loadkeys "{keymap}"')
    font = 'ter-v16b'
    os.system('setfont ter-v16b')
    dimensions = os.popen('stty size').read().split(" ")
    if dimensions is not None and len(dimensions) > 0 and int(dimensions[0]) >= 80:
        font = 'ter-v32b'
        os.system('setfont ter-v32b')
    if global_language == "FR":
        os.system('sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /etc/locale.gen')
        os.system('locale-gen')
        os.putenv('LANG', 'fr_FR.UTF-8')
        os.putenv('LANGUAGE', 'fr_FR.UTF-8')
    else:
        os.putenv('LANG', 'en_US.UTF-8')
        os.putenv('LANGUAGE', 'en_US.UTF-8')
    return font


def setup_chroot_keyboard(layout: str):
    """
    The method to set the X keyboard of the chrooted system.
    :param layout:
    """
    content = [
        "Section \"InputClass\"\n",
        "    Identifier \"system-keyboard\"\n",
        "    MatchIsKeyboard \"on\"\n",
        f"    Option \"XkbLayout\" \"{layout}\"\n",
        "EndSection\n"
    ]
    os.system("mkdir --parents /mnt/etc/X11/xorg.conf.d/")
    with open("/mnt/etc/X11/xorg.conf.d/00-keyboard.conf", "w", encoding="UTF-8") as keyboard_config_file:
        keyboard_config_file.writelines(content)


def configure_zram():
    """
    The method to configure zram generator.
    """
    content = [
        "[zram0]\n",
        "zram-size = ram / 2\n"
    ]
    with open("/mnt/etc/systemd/zram-generator.conf", "w", encoding="UTF-8") as zram_config_file:
        zram_config_file.writelines(content)


def ask_swapfile_size(disk: Disk) -> str:
    """
    The method to ask the user for the swapfile size.
    :return:
    """
    swapfile_ok = False
    swapfile_size = ""
    swapfile_size_pattern = re.compile("^(\\d*[.,]\\d+|\\d+)([GMk])$")
    default_swapfile_size = to_iec(int(disk.total / 32))
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


def get_default_format() -> str:
    """
    The method to get the default format type.
    :return:
    """
    return "ext4"


def get_supported_format_types() -> []:
    """
    The method to get all supported format types.
    :return:
    """
    return ["ext4", "btrfs"]


def ask_format_type() -> str:
    """
    The method to ask the user for the format type.
    :return:
    """
    default_format_type = get_default_format()
    format_type_ok = False
    format_type = None
    print_step(_("Supported format types : "), clear=False)
    print_sub_step(", ".join(get_supported_format_types()))
    while not format_type_ok:
        format_type = prompt_ln(
            _("Which format type do you want ? (%s) : ") % default_format_type, default=default_format_type).lower()
        if format_type in get_supported_format_types():
            format_type_ok = True
        else:
            print_error(_("Format type '%s' is not supported.") % format_type, do_pause=False)
            continue
    return format_type


def get_main_file_systems() -> [str]:
    return ["btrfs-progs", "dosfstools", "exfatprogs", "f2fs-tools", "e2fsprogs", "jfsutils", "nilfs-utils",
            "ntfs-3g", "reiserfsprogs", "udftools", "xfsprogs"]


def get_main_fonts() -> [str]:
    return ["gnu-free-fonts", "noto-fonts", "ttf-bitstream-vera", "ttf-dejavu", "ttf-hack", "ttf-droid",
            "ttf-fira-code", "ttf-fira-mono", "ttf-fira-sans", "ttf-font-awesome", "ttf-inconsolata",
            "ttf-input", "ttf-liberation", "ttf-nerd-fonts-symbols", "ttf-opensans", "ttf-roboto",
            "ttf-roboto-mono", "ttf-ubuntu-font-family", "ttf-jetbrains-mono"]


def manual_partitioning(bios: str) -> {}:
    """
    The method to proceed to the manual partitioning.
    :param bios:
    :return:
    """
    partitioning_info = {"partitions": [], "part_type": {}, "part_mount_point": {}, "part_format": {},
                         "part_format_type": {}, "root_partition": None, "swapfile_size": None, "main_disk": None}
    user_answer = False
    partitioned_disks = set()
    while not user_answer:
        print_step(_("Manual partitioning :"))
        print_sub_step(_("Partitioned drives so far : %s") % " ".join(partitioned_disks))
        os.system('fdisk -l')
        target_disk = prompt(
            _("Which drive do you want to partition ? (type the entire name, for example '/dev/sda') : "))
        if not os.path.exists(target_disk):
            print_error(_("The chosen target drive doesn't exist."))
            continue
        partitioned_disks.add(target_disk)
        os.system(f'cfdisk "{target_disk}"')
        print_step(_("Manual partitioning :"))
        print_sub_step(_("Partitioned drives so far : %s") % " ".join(partitioned_disks))
        os.system('fdisk -l')
        other_drive = prompt_bool(_("Do you want to partition an other drive ? (y/N) : "), default=False)
        if other_drive:
            continue
        for disk in partitioned_disks:
            detected_partitions = os.popen(
                f'lsblk -nl "{disk}" -o PATH,PARTTYPENAME | grep -iE "linux|efi|swap" | awk \'{{print $1}}\'').read()
            for partition in detected_partitions.splitlines():
                partitioning_info["partitions"].append(partition)
        print_step(_("Detected target drive partitions : %s") % " ".join(partitioning_info["partitions"]))
        for partition in partitioning_info["partitions"]:
            print_sub_step(_("Partition : %s") % re.sub('\n', '', os.popen(
                f'lsblk -nl "{partition}" -o PATH,SIZE,PARTTYPENAME').read()))
            if bios:
                partition_type = prompt(
                    _("What is the role of this partition ? (1: Root, 2: Home, 3: Swap, 4: Not used, other: Other) : "))
            else:
                partition_type = prompt(
                    _("What is the role of this partition ? (0: EFI, 1: Root, 2: Home, 3: Swap, 4: Not used, "
                      "other: Other) : "))
            if not bios and partition_type == "0":
                partitioning_info["part_type"][partition] = "EFI"
                partitioning_info["part_mount_point"][partition] = "/boot/efi"
                partitioning_info["part_format"][partition] = prompt_bool(_("Format the EFI partition ? (Y/n) : "))
                if partitioning_info["part_format"].get(partition):
                    partitioning_info["part_format_type"][partition] = "vfat"
            elif partition_type == "1":
                partitioning_info["part_type"][partition] = "ROOT"
                partitioning_info["part_mount_point"][partition] = "/"
                partitioning_info["part_format_type"][partition] = ask_format_type()
                partitioning_info["root_partition"] = partition
                main_disk_label = re.sub('\\s+', '', os.popen(f'lsblk -ndo PKNAME {partition}').read())
                partitioning_info["main_disk"] = f'/dev/{main_disk_label}'
            elif partition_type == "2":
                partitioning_info["part_type"][partition] = "HOME"
                partitioning_info["part_mount_point"][partition] = "/home"
                partitioning_info["part_format"][partition] = prompt_bool(_("Format the Home partition ? (Y/n) : "))
                if partitioning_info["part_format"].get(partition):
                    partitioning_info["part_format_type"][partition] = ask_format_type()
            elif partition_type == "3":
                partitioning_info["part_type"][partition] = "SWAP"
            elif partition_type == "4":
                continue
            else:
                partitioning_info["part_type"][partition] = "OTHER"
                partitioning_info["part_mount_point"][partition] = prompt(
                    _("What is the mounting point of this partition ? : "))
                partitioning_info["part_format"][partition] = prompt_bool(
                    _("Format the %s partition ? (Y/n) : ") % partition)
                if partitioning_info["part_format"].get(partition):
                    partitioning_info["part_format_type"][partition] = ask_format_type()
        if not bios and "EFI" not in partitioning_info["part_type"].values():
            print_error(_("The EFI partition is required for system installation."))
            partitioning_info["partitions"].clear()
            partitioned_disks.clear()
            continue
        if "ROOT" not in partitioning_info["part_type"].values():
            print_error(_("The Root partition is required for system installation."))
            partitioning_info["partitions"].clear()
            partitioned_disks.clear()
            continue
        if "SWAP" not in partitioning_info["part_type"].values():
            partitioning_info["swapfile_size"] = ask_swapfile_size(Disk(partitioning_info["main_disk"]))
        print_step(_("Summary of choices :"))
        for partition in partitioning_info["partitions"]:
            if partitioning_info["part_format"].get(partition):
                formatting = _("yes")
            else:
                formatting = _("no")
            if partitioning_info["part_type"].get(partition) == "EFI":
                print_sub_step(_("EFI partition : %s (mounting point : %s, format %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition), formatting,
                                  partitioning_info["part_format_type"].get(partition)))
            if partitioning_info["part_type"].get(partition) == "ROOT":
                print_sub_step(_("ROOT partition : %s (mounting point : %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition),
                                  partitioning_info["part_format_type"].get(partition)))
            if partitioning_info["part_type"].get(partition) == "HOME":
                print_sub_step(_("Home partition : %s (mounting point : %s, format %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition), formatting,
                                  partitioning_info["part_format_type"].get(partition)))
            if partitioning_info["part_type"].get(partition) == "SWAP":
                print_sub_step(_("Swap partition : %s") % partition)
            if partitioning_info["part_type"].get(partition) == "OTHER":
                print_sub_step(_("Other partition : %s (mounting point : %s, format %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition), formatting,
                                  partitioning_info["part_format_type"].get(partition)))
        if "SWAP" not in partitioning_info["part_type"].values() and partitioning_info["swapfile_size"] is not None:
            print_sub_step(_("Swapfile size : %s") % partitioning_info["swapfile_size"])
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
        if not user_answer:
            partitioning_info["partitions"].clear()
            partitioned_disks.clear()
    return partitioning_info


def build_partition_name(disk: str, index: str):
    """
    A method to build a partition name with a disk and an index.
    :param disk:
    :param index:
    :return:
    """
    return (f'{disk}{index}', f'{disk}p{index}')["nvme" in disk]


def to_iec(size: int) -> str:
    """
    The method to convert a size in iec format.
    """
    return re.sub('\\s', '', os.popen(f'printf "{size}" | numfmt --to=iec').read())


def from_iec(size: str) -> int:
    """
    The method to convert an iec formatted size in bytes.
    """
    return int(re.sub('\\s', '', os.popen(f'printf "{size}" | numfmt --from=iec').read()))


def auto_partitioning(bios: str) -> {}:
    """
    The method to proceed to the automatic partitioning.
    :param bios:
    :return:
    """
    partitioning_info = {"partitions": [], "part_type": {}, "part_mount_point": {}, "part_format": {},
                         "part_format_type": {}, "root_partition": None, "swapfile_size": None, "main_disk": None}
    user_answer = False
    while not user_answer:
        print_step(_("Automatic partitioning :"))
        os.system("fdisk -l")
        target_disk = prompt(
            _("On which drive should Archlinux be installed ? (type the entire name, for example '/dev/sda') : "))
        if target_disk == "":
            print_error(_("You need to choose a target drive."))
            continue
        if not os.path.exists(target_disk):
            print_error(_("You need to choose a target drive."))
            continue
        partitioning_info["main_disk"] = target_disk
        disk = Disk(target_disk)
        swap_type = prompt(_("What type of Swap do you want ? (1: Partition, 2: None, other: File) : "))
        want_home = prompt_bool(_("Do you want a separated Home ? (Y/n) : "))
        part_format_type = ask_format_type()
        efi_partition = disk.get_efi_partition()
        if not bios \
                and len(disk.partitions) > 0 \
                and efi_partition.path != "" \
                and efi_partition.fs_type == "vfat" \
                and disk.free_space > from_iec("32G"):
            want_dual_boot = prompt_bool(_("Do you want to install Arch Linux next to other systems ? (Y/n) : "))
        else:
            want_dual_boot = False
        if want_dual_boot:
            root_size = to_iec(int(disk.free_space / 4))
            swap_size = to_iec(int(disk.free_space / 32))
        else:
            root_size = to_iec(int(disk.total / 4))
            swap_size = to_iec(int(disk.total / 32))
        if swap_type != "1":
            if swap_type == "2":
                swap_size = None
            partitioning_info["swapfile_size"] = swap_size
        auto_part_str = ""
        index = 0
        if bios:
            # DOS LABEL
            auto_part_str += "o\n"  # Create a new empty DOS partition table
            # BOOT
            auto_part_str += "n\n"  # Add a new partition
            auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += "+1G\n"  # Last sector (Accept default: varies)
            auto_part_str += "a\n"  # Toggle bootable flag
            index += 1
            partition = build_partition_name(target_disk, str(index))
            partitioning_info["part_type"][partition] = "OTHER"
            partitioning_info["part_mount_point"][partition] = "/boot"
            partitioning_info["part_format"][partition] = True
            partitioning_info["part_format_type"][partition] = part_format_type
            partitioning_info["partitions"].append(partition)
        else:
            if not want_dual_boot:
                # GPT LABEL
                auto_part_str += "g\n"  # Create a new empty GPT partition table
                # EFI
                auto_part_str += "n\n"  # Add a new partition
                auto_part_str += " \n"  # Partition number (Accept default: auto)
                auto_part_str += " \n"  # First sector (Accept default: 1)
                auto_part_str += "+512M\n"  # Last sector (Accept default: varies)
                auto_part_str += "t\n"  # Change partition type
                auto_part_str += " \n"  # Partition number (Accept default: auto)
                auto_part_str += "1\n"  # Type EFI System
                index += 1
                partition = build_partition_name(target_disk, str(index))
                partitioning_info["part_format"][partition] = True
                partitioning_info["part_format_type"][partition] = "vfat"
            else:
                index += len(disk.partitions)
                partition = efi_partition.path
                partitioning_info["part_format"][partition] = False
            partitioning_info["part_type"][partition] = "EFI"
            partitioning_info["part_mount_point"][partition] = "/boot/efi"
            partitioning_info["partitions"].append(partition)
        if swap_type == "1":
            # SWAP
            auto_part_str += "n\n"  # Add a new partition
            if bios:
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += f'+{swap_size}\n'  # Last sector (Accept default: varies)
            auto_part_str += "t\n"  # Change partition type
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            if bios:
                auto_part_str += "82\n"  # Type Linux Swap
            else:
                auto_part_str += "19\n"  # Type Linux Swap
            index += 1
            partition = build_partition_name(target_disk, str(index))
            partitioning_info["part_type"][partition] = "SWAP"
            partitioning_info["partitions"].append(partition)
        if want_home:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if bios:
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += f'+{root_size}\n'  # Last sector (Accept default: varies)
            index += 1
            partition = build_partition_name(target_disk, str(index))
            partitioning_info["part_type"][partition] = "ROOT"
            partitioning_info["part_mount_point"][partition] = "/"
            partitioning_info["part_format_type"][partition] = part_format_type
            partitioning_info["root_partition"] = partition
            partitioning_info["partitions"].append(partition)
            # HOME
            auto_part_str += "n\n"  # Add a new partition
            if bios:
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            index += 1
            partition = build_partition_name(target_disk, str(index))
            partitioning_info["part_type"][partition] = "HOME"
            partitioning_info["part_mount_point"][partition] = "/home"
            partitioning_info["part_format"][partition] = True
            partitioning_info["part_format_type"][partition] = part_format_type
            partitioning_info["partitions"].append(partition)
        else:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if bios:
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            index += 1
            partition = build_partition_name(target_disk, str(index))
            partitioning_info["part_type"][partition] = "ROOT"
            partitioning_info["part_mount_point"][partition] = "/"
            partitioning_info["part_format_type"][partition] = part_format_type
            partitioning_info["root_partition"] = partition
            partitioning_info["partitions"].append(partition)
        # WRITE
        auto_part_str += "w\n"

        print_step(_("Summary of choices :"), clear=False)
        for partition in partitioning_info["partitions"]:
            if partitioning_info["part_format"].get(partition):
                formatting = _("yes")
            else:
                formatting = _("no")
            if partitioning_info["part_type"].get(partition) == "EFI":
                print_sub_step(_("EFI partition : %s (mounting point : %s, format %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition), formatting,
                                  partitioning_info["part_format_type"].get(partition)))
            if partitioning_info["part_type"].get(partition) == "ROOT":
                print_sub_step(_("ROOT partition : %s (mounting point : %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition),
                                  partitioning_info["part_format_type"].get(partition)))
            if partitioning_info["part_type"].get(partition) == "HOME":
                print_sub_step(_("Home partition : %s (mounting point : %s, format %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition), formatting,
                                  partitioning_info["part_format_type"].get(partition)))
            if partitioning_info["part_type"].get(partition) == "SWAP":
                print_sub_step(_("Swap partition : %s") % partition)
            if partitioning_info["part_type"].get(partition) == "OTHER":
                print_sub_step(_("Other partition : %s (mounting point : %s, format %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition), formatting,
                                  partitioning_info["part_format_type"].get(partition)))
        if "SWAP" not in partitioning_info["part_type"].values() and swap_size is not None:
            print_sub_step(_("Swapfile size : %s") % swap_size)
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
        if not user_answer:
            partitioning_info["partitions"].clear()
        else:
            os.system(f'echo -e "{auto_part_str}" | fdisk "{target_disk}" &>/dev/null')
    return partitioning_info


def environment_config(detected_language: str) -> {}:
    """
    The method to get environment configurations from the user.
    :param detected_language:
    :return:
    """
    pre_launch_info = {"global_language": None, "keymap": None, "bios": None}
    user_answer = False
    while not user_answer:
        print_step(_("Welcome to the archlinux-install script !"))
        pre_launch_info["bios"] = not os.path.exists("/sys/firmware/efi")
        if pre_launch_info["bios"]:
            print_error(
                _("BIOS detected ! The script will act accordingly. Don't forget to select a DOS label type before "
                  "partitioning."))

        print_step(_("Environment configuration : "), clear=False)

        supported_global_languages = ["FR", "EN"]
        if detected_language == "fr-FR":
            default_language = "FR"
        else:
            default_language = "EN"

        print_step(_("Supported languages : "), clear=False)
        print_sub_step(", ".join(supported_global_languages))
        print('')
        global_language_ok = False
        pre_launch_info["global_language"] = None
        pre_launch_info["keymap"] = None
        while not global_language_ok:
            pre_launch_info["global_language"] = prompt_ln(
                _("Choose your installation's language (%s) : ") % default_language,
                default=default_language).upper()
            if pre_launch_info["global_language"] in supported_global_languages:
                global_language_ok = True
            else:
                print_error(_("Global language '%s' is not supported.") % pre_launch_info["global_language"],
                            do_pause=False)
                continue

        if detected_language == "fr-FR":
            default_keymap = "fr-latin9"
        else:
            default_keymap = "de-latin1"

        keymap_ok = False
        while not keymap_ok:
            pre_launch_info["keymap"] = prompt_ln(_("Type your installation's keymap (%s) : ") % default_keymap,
                                                  default=default_keymap)
            if os.system(f'localectl list-keymaps | grep "^{pre_launch_info["keymap"]}$" &>/dev/null') == 0:
                keymap_ok = True
            else:
                print_error(_("Keymap %s doesn't exist.") % pre_launch_info["keymap"])
                continue

        print_step(_("Summary of choices :"), clear=False)
        print_sub_step(_("Your installation's language : %s") % pre_launch_info["global_language"])
        print_sub_step(_("Your installation's keymap : %s") % pre_launch_info["keymap"])
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
    return pre_launch_info


def ask_password(username: str = "root") -> str:
    """
    A method to ask a password to the user.
    :param username:
    :return:
    """
    password_confirm = None
    password = ""
    while password != password_confirm:
        print_sub_step(_("%s password configuration : ") % username)
        password = prompt_passwd(_("Enter the %s password : ") % username)
        password_confirm = prompt_passwd(_("Re-enter the %s password to confirm : ") % username)
        if password != password_confirm:
            print_error(_("Passwords entered don't match."))
    return password


def system_config(detected_timezone) -> {}:
    """
    The method to get system configurations from the user.
    :param detected_timezone:
    :return:
    """
    system_info = {}
    user_answer = False
    supported_desktops = ["gnome", "plasma", "xfce", "budgie", "cinnamon", "cutefish", "deepin", "lxqt", "mate",
                          "enlightenment", "i3", "sway", _("none")]
    while not user_answer:
        print_step(_("System configuration : "))
        system_info["hostname"] = prompt(_("What will be your hostname (archlinux) : "), default="archlinux")
        system_info["lts_kernel"] = prompt_bool(_("Install LTS Linux kernel ? (y/N) : "), default=False)
        system_info["nvidia_driver"] = prompt_bool(_("Install proprietary Nvidia driver ? (y/N) : "), default=False)
        system_info["terminus_font"] = prompt_bool(_("Install terminus console font ? (y/N) : "), default=False)

        print_step(_("Supported desktop environments : "), clear=False)
        print_sub_step(", ".join(supported_desktops))
        print('')
        desktop_ok = False
        while not desktop_ok:
            desktop = prompt_ln(
                _("Install a desktop environment ? (%s) : ") % _("none"), default=_("none")).lower()
            if desktop in supported_desktops:
                desktop_ok = True
                system_info["desktop"] = desktop
            else:
                print_error(_("Desktop environment '%s' is not supported.") % desktop, do_pause=False)
                continue

        if system_info["desktop"] in {"gnome", "plasma", "xfce", "deepin", "mate"}:
            system_info["want_minimal"] = prompt_bool(
                _("Install a minimal environment ? (y/N/?) : "),
                default=False,
                help_msg=_("If yes, the script will not install any extra packages, only base packages."))

        system_info["plasma_wayland"] = False
        if system_info["desktop"] == "plasma":
            system_info["plasma_wayland"] = prompt_bool(_("Install Wayland support for the plasma session ? (y/N) : "),
                                                        default=False)
        system_info["cups"] = prompt_bool(_("Install Cups ? (y/N) : "), default=False)
        system_info["grml_zsh"] = prompt_bool(_("Install ZSH with GRML configuration ? (y/N/?) : "), default=False,
                                              help_msg=_(
                                                  "If yes, the script will install the ZSH shell with GRML "
                                                  "configuration. GRML is a ZSH pre-configuration used by Archlinux's "
                                                  "live environment."))
        system_info["main_fonts"] = \
            prompt_bool(_("Install a set of main fonts ? (y/N/?) : "), default=False,
                        help_msg=_("If yes, the following packages will be installed :\n%s") % " ".join(
                            get_main_fonts()))
        system_info["main_file_systems"] = prompt_bool(_("Install main file systems support ? (y/N/?) : "),
                                                       default=False, help_msg=_(
                "If yes, the following packages will be installed :\n%s") % " ".join(get_main_file_systems()))
        system_info["zram"] = prompt_bool(_("Install and enable ZRAM ? (y/N/?) : "), default=False, help_msg=_(
            "ZRAM is a process to compress datas directly in the RAM instead of moving them in a swap. Enabled ZRAM "
            "will allow you to compress up to half of your RAM before having to swap. This method is more efficient "
            "than the swap and do not use your disk but is more CPU demanding. ZRAM is fully compatible with a swap, "
            "it just has a higher priority."))
        default_timezone_file = f'/usr/share/zoneinfo/{detected_timezone}'
        system_info["timezone"] = prompt_ln(_("Your timezone (%s) : ") % default_timezone_file,
                                            default=default_timezone_file)
        system_info["user_name"] = prompt_ln(_("Would you like to add a user? (type username, leave blank if none) : "))
        system_info["user_full_name"] = ""
        if system_info["user_name"] != "":
            system_info["user_full_name"] = prompt_ln(
                _("What is the %s's full name (type the entire full name, leave blank if none) : ") % system_info[
                    "user_name"])

        pkgs_select_ok = False
        while not pkgs_select_ok:
            system_info["more_pkgs"] = set()
            more_pkgs_str = prompt_ln(
                _("Install more packages ? (type extra packages full names, example : 'htop neofetch', leave blank if "
                  "none) : "))
            pkgs_select_ok = True
            if more_pkgs_str != "":
                for pkg in more_pkgs_str.split():
                    if os.system(f'pacman -Si {pkg} &>/dev/null') != 0:
                        pkgs_select_ok = False
                        print_error(_("Package %s doesn't exist.") % pkg)
                        break
                    system_info["more_pkgs"].add(pkg)

        system_info["root_password"] = ask_password()
        if system_info["user_name"] != "":
            system_info["user_password"] = ask_password(system_info["user_name"])

        system_info["microcodes"] = re.sub(
            '\\s+', '', os.popen('grep </proc/cpuinfo "vendor" | uniq').read()).split(":")[1]

        print_step(_("Summary of choices :"))
        print_sub_step(_("Your hostname : %s") % system_info["hostname"])
        if system_info["microcodes"] in {"GenuineIntel", "AuthenticAMD"}:
            print_sub_step(_("Microcodes to install : %s") % system_info["microcodes"])
        if system_info["lts_kernel"]:
            print_sub_step(_("Install LTS Linux kernel."))
        if system_info["nvidia_driver"]:
            print_sub_step(_("Install proprietary Nvidia driver."))
        if system_info["terminus_font"]:
            print_sub_step(_("Install terminus console font."))
        print_sub_step(_("Desktop environment : %s") % system_info["desktop"])
        if system_info["desktop"] in {"gnome", "plasma", "xfce", "deepin", "mate"} and system_info["want_minimal"]:
            print_sub_step(_("Install a minimal environment (no extra packages, only base)."))
        if system_info["desktop"] == "plasma" and system_info["plasma_wayland"]:
            print_sub_step(_("Install Wayland support for the plasma session."))
        if system_info["cups"]:
            print_sub_step(_("Install Cups."))
        if system_info["grml_zsh"]:
            print_sub_step(_("Install ZSH with GRML configuration."))
        if system_info["main_fonts"]:
            print_sub_step(_("Install a set of main fonts."))
        if system_info["main_file_systems"]:
            print_sub_step(_("Install main file systems support."))
        if system_info["zram"]:
            print_sub_step(_("Install and enable ZRAM."))
        print_sub_step(_("Your timezone : %s") % system_info["timezone"])
        if system_info["user_name"] != "":
            print_sub_step(_("Additional user name : %s") % system_info["user_name"])
            if system_info["user_full_name"] != "":
                print_sub_step(_("User's full name : %s") % system_info["user_full_name"])
        if system_info["more_pkgs"]:
            print_sub_step(_("More packages to install : %s") % " ".join(system_info["more_pkgs"]))
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
    return system_info


def umount_partitions():
    """
    A method to unmount all mounted partitions.
    """
    print_step(_("Unmounting partitions..."), clear=False)
    swap = re.sub('\\s', '', os.popen('swapon --noheadings | awk \'{print $1}\'').read())
    if swap != "":
        os.system(f'swapoff {swap} &>/dev/null')

    os.system('umount -R /mnt &>/dev/null')


def format_partition(partition: str, format_type: str, mount_point: str, formatting: bool):
    """
    A method to compute and return an mkfs command.
    """
    match format_type:
        case "vfat":
            if formatting:
                os.system(f'mkfs.vfat "{partition}"')
            os.system(f'mkdir -p "/mnt{mount_point}"')
            os.system(f'mount "{partition}" "/mnt{mount_point}"')
        case "btrfs":
            if formatting:
                os.system(f'mkfs.btrfs -f "{partition}"')
            os.system(f'mkdir -p "/mnt{mount_point}"')
            os.system(f'mount -o compress=zstd "{partition}" "/mnt{mount_point}"')
        case _:
            if formatting:
                os.system(f'mkfs.ext4 "{partition}"')
            os.system(f'mkdir -p "/mnt{mount_point}"')
            os.system(f'mount "{partition}" "/mnt{mount_point}"')


def main(pre_launch_info):
    """ The main method. """
    system_info = system_config(pre_launch_info["detected_timezone"])
    system_info["btrfs_in_use"] = False

    print_step(_("Partitioning :"))
    want_auto_part = prompt_bool(_("Do you want an automatic partitioning ? (y/N) : "), default=False)
    if want_auto_part:
        partitioning_info = auto_partitioning(pre_launch_info["bios"])
    else:
        partitioning_info = manual_partitioning(
            pre_launch_info["bios"])

    print_step(_("Formatting and mounting partitions..."), clear=False)

    format_partition(partitioning_info["root_partition"],
                     partitioning_info["part_format_type"][partitioning_info["root_partition"]],
                     partitioning_info["part_mount_point"][partitioning_info["root_partition"]], True)
    if partitioning_info["part_format_type"][partitioning_info["root_partition"]] == "btrfs":
        system_info["btrfs_in_use"] = True

    for partition in partitioning_info["partitions"]:
        if partitioning_info["part_format_type"].get(partition) == "btrfs":
            system_info["btrfs_in_use"] = True
        if not pre_launch_info["bios"] and partitioning_info["part_type"].get(partition) == "EFI":
            format_partition(partition, partitioning_info["part_format_type"].get(partition),
                             partitioning_info["part_mount_point"].get(partition),
                             partitioning_info["part_format"].get(partition))
        elif partitioning_info["part_type"].get(partition) == "HOME":
            format_partition(partition, partitioning_info["part_format_type"].get(partition),
                             partitioning_info["part_mount_point"].get(partition),
                             partitioning_info["part_format"].get(partition))
        elif partitioning_info["part_type"].get(partition) == "SWAP":
            os.system(f'mkswap "{partition}"')
            os.system(f'swapon "{partition}"')
        elif partitioning_info["part_type"].get(partition) == "OTHER":
            format_partition(partition, partitioning_info["part_format_type"].get(partition),
                             partitioning_info["part_mount_point"].get(partition),
                             partitioning_info["part_format"].get(partition))

    print_step(_("Updating mirrors..."), clear=False)
    os.system(
        f'reflector --save /etc/pacman.d/mirrorlist --threads $(nproc --all) --protocol https --age 12 --country '
        f'"{pre_launch_info["detected_country_code"]}" --fastest 10 --sort rate')

    base_pkgs = set()
    base_pkgs.update(["base", "base-devel", "linux-firmware"])
    if system_info["lts_kernel"]:
        base_pkgs.update(["linux-lts", "linux-lts-headers"])
    else:
        base_pkgs.update(["linux", "linux-headers"])

    pkgs = set()
    pkgs.update(["man-db", "man-pages", "texinfo", "nano", "vim", "git", "curl", "grub", "os-prober", "efibootmgr",
                 "networkmanager", "xdg-user-dirs", "reflector", "numlockx", "net-tools", "polkit", "pacman-contrib"])
    if pre_launch_info["global_language"].lower() != "en" and os.system(
            f"pacman -Si man-pages-{pre_launch_info['global_language'].lower()} &>/dev/null") == 0:
        pkgs.add(f"man-pages-{pre_launch_info['global_language'].lower()}")
    if system_info["btrfs_in_use"]:
        pkgs.add("btrfs-progs")
    if system_info["microcodes"] == "GenuineIntel":
        pkgs.add("intel-ucode")
    if system_info["microcodes"] == "AuthenticAMD":
        pkgs.add("amd-ucode")
    if system_info["nvidia_driver"] and system_info["lts_kernel"]:
        pkgs.add("nvidia-lts")
    elif system_info["nvidia_driver"] and not system_info["lts_kernel"]:
        pkgs.add("nvidia")
    if system_info["terminus_font"]:
        pkgs.add("terminus-font")
    if system_info["desktop"] == "gnome":
        pkgs.update(["gnome", "alsa-utils", "pulseaudio", "pulseaudio-alsa", "xdg-desktop-portal",
                     "xdg-desktop-portal-gnome", "qt5-wayland"])
        if system_info["want_minimal"] is not True:
            pkgs.add("gnome-extra")
    elif system_info["desktop"] == "plasma":
        pkgs.update(["plasma", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa",
                     "xdg-desktop-portal", "xdg-desktop-portal-kde"])
        if system_info["plasma_wayland"]:
            pkgs.update(["plasma-wayland-session", "qt5-wayland"])
            if system_info["nvidia_driver"]:
                pkgs.add("egl-wayland")
        if system_info["want_minimal"] is not True:
            pkgs.add("kde-applications")
    elif system_info["desktop"] == "xfce":
        pkgs.update(
            ["xfce4", "lightdm", "lightdm-gtk-greeter", "lightdm-gtk-greeter-settings", "xorg-server",
             "alsa-utils", "pulseaudio", "pulseaudio-alsa", "pavucontrol", "network-manager-applet"])
        if system_info["want_minimal"] is not True:
            pkgs.add("xfce4-goodies")
    elif system_info["desktop"] == "budgie":
        pkgs.update(["budgie-desktop", "budgie-desktop-view", "budgie-screensaver", "gnome-control-center",
                     "network-manager-applet", "gnome", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa",
                     "pavucontrol"])
    elif system_info["desktop"] == "cinnamon":
        pkgs.update(["cinnamon", "metacity", "gnome-shell", "gnome-terminal", "blueberry", "cinnamon-translations",
                     "gnome-panel", "system-config-printer", "wget", "lightdm", "lightdm-gtk-greeter",
                     "lightdm-gtk-greeter-settings", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa",
                     "pavucontrol"])
    elif system_info["desktop"] == "cutefish":
        pkgs.update(["cutefish", "sddm", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa", "pavucontrol"])
    elif system_info["desktop"] == "deepin":
        pkgs.update(["deepin", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa"])
        if system_info["want_minimal"] is not True:
            pkgs.add("deepin-extra")
    elif system_info["desktop"] == "lxqt":
        pkgs.update(
            ["lxqt", "sddm", "xorg-server", "breeze-icons", "xdg-utils", "xscreensaver", "xautolock", "libpulse",
             "alsa-lib", "libstatgrab", "libsysstat", "lm_sensors", "system-config-printer", "alsa-utils", "pulseaudio",
             "pulseaudio-alsa", "pavucontrol", "network-manager-applet"])
    elif system_info["desktop"] == "mate":
        pkgs.update(
            ["mate", "lightdm", "lightdm-gtk-greeter", "lightdm-gtk-greeter-settings", "xorg-server",
             "alsa-utils", "pulseaudio", "pulseaudio-alsa", "network-manager-applet"])
        if system_info["want_minimal"] is not True:
            pkgs.add("mate-extra")
    elif system_info["desktop"] == "enlightenment":
        pkgs.update(
            ["enlightenment", "terminology", "xorg-server", "xorg-xinit", "alsa-utils", "pulseaudio", "pulseaudio-alsa",
             "pavucontrol", "system-config-printer", "network-manager-applet", "acpid"])
    elif system_info["desktop"] == "i3":
        pkgs.update(
            ["i3", "rofi", "dmenu", "perl", "alacritty", "xorg-server", "xorg-xinit", "alsa-utils", "pulseaudio",
             "pulseaudio-alsa", "pavucontrol", "system-config-printer", "network-manager-applet", "acpid"])
    elif system_info["desktop"] == "sway":
        pkgs.update(["sway", "rofi", "dmenu", "alacritty", "grim", "i3status", "mako", "slurp", "swayidle", "swaylock",
                     "waybar", "swaybg", "wf-recorder", "xorg-xwayland", "alsa-utils", "pulseaudio",
                     "pulseaudio-alsa", "pavucontrol", "system-config-printer", "network-manager-applet", "acpid"])
    if system_info["cups"]:
        pkgs.update(
            ["cups", "cups-pdf", "avahi", "samba", "foomatic-db-engine", "foomatic-db", "foomatic-db-ppds",
             "foomatic-db-nonfree-ppds", "foomatic-db-gutenprint-ppds", "gutenprint", "ghostscript"])
    if system_info["grml_zsh"]:
        pkgs.update(["zsh", "zsh-completions", "grml-zsh-config"])
    else:
        pkgs.add("bash-completion")
    if system_info["main_fonts"]:
        pkgs.update(get_main_fonts())
    if system_info["main_file_systems"]:
        pkgs.update(get_main_file_systems())
    if system_info["zram"]:
        pkgs.add("zram-generator")
    if len(system_info["more_pkgs"]) > 0:
        pkgs.update(system_info["more_pkgs"])

    print_step(_("Installation of the base..."), clear=False)
    subprocess.run(f'pacstrap /mnt {" ".join(base_pkgs)}', shell=True, check=True)

    print_step(_("System configuration..."), clear=False)
    os.system('sed -i "s|#en_US.UTF-8 UTF-8|en_US.UTF-8 UTF-8|g" /mnt/etc/locale.gen')
    os.system('sed -i "s|#en_US ISO-8859-1|en_US ISO-8859-1|g" /mnt/etc/locale.gen')
    if pre_launch_info["global_language"] == "FR":
        os.system('sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /mnt/etc/locale.gen')
        os.system('sed -i "s|#fr_FR ISO-8859-1|fr_FR ISO-8859-1|g" /mnt/etc/locale.gen')
        os.system('echo "LANG=fr_FR.UTF-8" >/mnt/etc/locale.conf')
    else:
        os.system('echo "LANG=en_US.UTF-8" >/mnt/etc/locale.conf')
    os.system(f'echo "KEYMAP={pre_launch_info["keymap"]}" >/mnt/etc/vconsole.conf')
    if system_info["terminus_font"]:
        os.system(f'echo "FONT={pre_launch_info["live_console_font"]}" >>/mnt/etc/vconsole.conf')
    os.system(f'echo "{system_info["hostname"]}" >/mnt/etc/hostname')
    os.system(f'''
        {{
            echo "127.0.0.1 localhost"
            echo "::1 localhost"
            echo "127.0.1.1 {system_info["hostname"]}.localdomain {system_info["hostname"]}"
        }} >>/mnt/etc/hostname
    ''')
    os.system('cp /etc/pacman.d/mirrorlist /mnt/etc/pacman.d/mirrorlist')

    print_step(_("Locales configuration..."), clear=False)
    os.system(f'arch-chroot /mnt bash -c "ln -sf {system_info["timezone"]} /etc/localtime"')
    os.system('arch-chroot /mnt bash -c "locale-gen"')

    print_step(_("Installation of the remaining packages..."), clear=False)
    os.system('sed -i "s|#Color|Color|g" /mnt/etc/pacman.conf')
    os.system('sed -i "s|#ParallelDownloads = 5|ParallelDownloads = 5\\nDisableDownloadTimeout|g" /mnt/etc/pacman.conf')
    subprocess.run(f'arch-chroot /mnt bash -c "pacman --noconfirm -S {" ".join(pkgs)}"', shell=True, check=True)

    if "SWAP" not in partitioning_info["part_type"].values() and partitioning_info["swapfile_size"] is not None:
        print_step(_("Creation and activation of the swapfile..."), clear=False)
        if partitioning_info["part_format_type"][partitioning_info["root_partition"]] == "btrfs":
            os.system(
                "btrfs subvolume create /mnt/swap && "
                "cd /mnt/swap && "
                "truncate -s 0 ./swapfile && "
                "chattr +C ./swapfile && "
                "btrfs property set ./swapfile compression none && "
                "cd -")
        else:
            os.system("mkdir -p /mnt/swap")
        os.system(f'fallocate -l "{partitioning_info["swapfile_size"]}" /mnt/swap/swapfile')
        os.system('chmod 600 /mnt/swap/swapfile')
        os.system('mkswap /mnt/swap/swapfile')
        os.system('swapon /mnt/swap/swapfile')

    print_step(_("Generating fstab..."), clear=False)
    os.system('genfstab -U /mnt >>/mnt/etc/fstab')

    print_step(_("Network configuration..."), clear=False)
    os.system('arch-chroot /mnt bash -c "systemctl enable NetworkManager"')
    os.system('arch-chroot /mnt bash -c "systemctl enable systemd-timesyncd"')

    print_step(_("Installation and configuration of the grub..."), clear=False)
    if pre_launch_info["bios"]:
        os.system(f'arch-chroot /mnt bash -c "grub-install --target=i386-pc {partitioning_info["main_disk"]}"')
    else:
        os.system(
            'arch-chroot /mnt bash -c "grub-install --target=x86_64-efi --efi-directory=/boot/efi '
            '--bootloader-id=\'Arch Linux\'"')
    os.system('arch-chroot /mnt bash -c "grub-mkconfig -o /boot/grub/grub.cfg"')
    os.system('sed -i "/^GRUB_CMDLINE_LINUX=.*/a GRUB_DISABLE_OS_PROBER=false" /mnt/etc/default/grub')
    if partitioning_info["part_format_type"][partitioning_info["root_partition"]] in {"ext4"}:
        os.system('sed -i "s|GRUB_DEFAULT=.*|GRUB_DEFAULT=saved|g" /mnt/etc/default/grub')
        os.system('sed -i "/^GRUB_DEFAULT=.*/a GRUB_SAVEDEFAULT=true" /mnt/etc/default/grub')

    print_step(_("Extra packages configuration if needed..."), clear=False)
    if system_info["desktop"] in {"gnome", "budgie"}:
        os.system('arch-chroot /mnt bash -c "systemctl enable gdm"')
    if system_info["desktop"] in {"plasma", "cutefish", "lxqt"}:
        os.system('arch-chroot /mnt bash -c "systemctl enable sddm"')
    if system_info["desktop"] in {"xfce", "cinnamon", "deepin", "mate"}:
        os.system('arch-chroot /mnt bash -c "systemctl enable lightdm"')
    if system_info["desktop"] in {"enlightenment", "i3", "sway"}:
        os.system('arch-chroot /mnt bash -c "systemctl enable acpid"')
    if system_info["desktop"] == "sway":
        if "fr" in pre_launch_info["keymap"]:
            os.system("echo 'XKB_DEFAULT_LAYOUT=fr' >> /mnt/etc/environment")
    if system_info["desktop"] in {"xfce", "cinnamon", "mate"}:
        os.system(
            'sed -i "s|#logind-check-graphical=false|logind-check-graphical=true|g" /mnt/etc/lightdm/lightdm.conf')
    if system_info["desktop"] != _("none"):
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")
    if system_info["cups"]:
        os.system('arch-chroot /mnt bash -c "systemctl enable avahi-daemon"')
        os.system('arch-chroot /mnt bash -c "systemctl enable cups"')
        os.system('arch-chroot /mnt bash -c "systemctl enable cups-browsed"')
    if system_info["zram"]:
        configure_zram()

    print_step(_("Users configuration..."), clear=False)
    print_sub_step(_("root account configuration..."))
    if system_info["grml_zsh"]:
        os.system('arch-chroot /mnt bash -c "chsh --shell /bin/zsh"')
    if system_info["root_password"] != "":
        os.system(f'arch-chroot /mnt bash -c "echo \'root:{system_info["root_password"]}\' | chpasswd"')
    if system_info["user_name"] != "":
        print_sub_step(_("%s account configuration...") % system_info["user_name"])
        os.system('sed -i "s|# %wheel ALL=(ALL:ALL) ALL|%wheel ALL=(ALL:ALL) ALL|g" /mnt/etc/sudoers')
        if system_info["grml_zsh"]:
            os.system(
                f'arch-chroot /mnt bash -c "useradd --shell=/bin/zsh --groups=wheel '
                f'--create-home {system_info["user_name"]}"')
        else:
            os.system(
                f'arch-chroot /mnt bash -c "useradd --shell=/bin/bash --groups=wheel '
                f'--create-home {system_info["user_name"]}"')
        if system_info["user_full_name"] != "":
            os.system(
                f'arch-chroot /mnt bash -c "chfn -f \'{system_info["user_full_name"]}\' {system_info["user_name"]}"')
        if system_info["user_password"] != "":
            os.system(
                f'arch-chroot /mnt bash -c "echo \'{system_info["user_name"]}:'
                f'{system_info["user_password"]}\' | chpasswd"')

    umount_partitions()

    print_step(_("Installation complete ! You can reboot your system."), clear=False)


def pre_launch_steps() -> {}:
    """
    The method to proceed to the pre-launch steps
    :return:
    """
    print_step(_("Running pre-launch steps : "), clear=False)
    os.system('sed -i "s|#Color|Color|g" /etc/pacman.conf')
    os.system('sed -i "s|#ParallelDownloads = 5|ParallelDownloads = 5\\nDisableDownloadTimeout|g" /etc/pacman.conf')
    print_sub_step(_("Synchronising repositories..."))
    os.system("pacman -Sy &>/dev/null")
    print_sub_step(_("Downloading and formatting translations..."))
    if not os.path.exists("fr.po"):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/rawleenc/archlinux-install/dev/locales/fr.po",
                                   "fr.po")
    os.system('msgfmt -o /usr/share/locale/fr/LC_MESSAGES/archlinux-install.mo fr.po &>/dev/null')
    print_sub_step(_("Querying IP geolocation informations..."))
    with urllib.request.urlopen('https://ipapi.co/json') as response:
        geoip_info = json.loads(response.read())
    detected_language = str(geoip_info["languages"]).split(",", maxsplit=1)[0]
    detected_timezone = geoip_info["timezone"]
    detected_country_code = geoip_info["country_code"]
    pre_launch_info = environment_config(detected_language)
    pre_launch_info["detected_country_code"] = detected_country_code
    pre_launch_info["detected_timezone"] = detected_timezone
    pre_launch_info["live_console_font"] = locale_setup(keymap=pre_launch_info["keymap"],
                                                        global_language=pre_launch_info["global_language"])
    return pre_launch_info


if __name__ == '__main__':
    _ = gettext.gettext
    try:
        PRE_LAUNCH_INFO = pre_launch_steps()
        if PRE_LAUNCH_INFO["global_language"] != "EN":
            translation = gettext.translation('archlinux-install', localedir='/usr/share/locale',
                                              languages=[PRE_LAUNCH_INFO["global_language"].lower()])
            translation.install()
            _ = translation.gettext
        main(PRE_LAUNCH_INFO)
    except KeyboardInterrupt:
        print_error(_("Script execution interrupted by the user !"), do_pause=False)
        umount_partitions()
    except subprocess.CalledProcessError:
        print_error(_("A subprocess execution failed !"), do_pause=False)
        umount_partitions()
