"""
The general utility methods and tools module
"""
import getpass
import json
import os
import re
from enum import StrEnum

from src.i18n import I18n
from src.options import FSFormat

RED = "\033[0;31m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
ORANGE = "\033[0;33m"
NOCOLOR = "\033[0m"

_ = I18n().gettext


def is_bios() -> bool:
    """
    Check if live system run on a bios.
    :return:
    """
    return not os.path.exists("/sys/firmware/efi")


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


def build_partition_name(disk_name: str, index: int) -> str or None:
    """
    A method to build a partition name with a disk and an index.
    :param disk_name:
    :param index:
    :return:
    """
    block_devices_str = os.popen('lsblk -J').read()
    block_devices_json = json.loads(block_devices_str)
    if block_devices_json is None or not isinstance(block_devices_json, dict) or "blockdevices" not in dict(
            block_devices_json):
        return None
    block_devices = dict(block_devices_json).get("blockdevices")
    if block_devices is None or not isinstance(block_devices, list):
        return None
    disk = next((d for d in block_devices if
                 d is not None and isinstance(d, dict) and "name" in d and dict(d).get("name") == os.path.basename(
                     disk_name)), None)
    if disk is None or not isinstance(disk, dict) or "children" not in dict(disk):
        return None
    partitions = dict(disk).get("children")
    if partitions is None or not isinstance(partitions, list) or len(list(partitions)) <= index:
        return None
    partition = list(partitions)[index]
    if partition is None or not isinstance(partition, dict) or "name" not in dict(partition):
        return None
    return f'/dev/{dict(partition).get("name")}'


def ask_format_type() -> str:
    """
    The method to ask the user for the format type.
    :return:
    """
    default_format_type = list(FSFormat)[0]
    format_type_ok = False
    format_type = None
    print_step(_("Supported format types : "), clear=False)
    print_sub_step(", ".join(list(FSFormat)))
    while not format_type_ok:
        format_type = prompt_ln(
            _("Which format type do you want ? (%s) : ") % default_format_type, default=default_format_type).lower()
        if format_type in FSFormat:
            format_type_ok = True
        else:
            print_error(_("Format type '%s' is not supported.") % format_type, do_pause=False)
            continue
    return format_type


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
        if user_input == "?" and help_msg and help_msg != "":
            print_help(help_msg)
            continue
        if user_input == "" and default:
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


def prompt_option(supported_msg: str, message: str, error_msg: str, options: type(StrEnum)) -> StrEnum or None:
    """
    A method to prompt for a bundle.
    :param supported_msg:
    :param message:
    :param error_msg:
    :param options:
    :return:
    """
    default_option = list(options)[0]
    print_step(supported_msg, clear=False)
    print_sub_step(", ".join(list(options)))
    print('')
    option_ok = False
    option = None
    while not option_ok:
        option_name = prompt_ln(
            message % default_option,
            default=default_option).lower()
        if option_name in options:
            option_ok = True
            option = options(option_name)
        else:
            print_error(error_msg % option_name, do_pause=False)
            continue
    return option


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
