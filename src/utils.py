"""
The general utility methods and tools module
"""
import encodings
import getpass
import glob
import json
import os
import re
import readline
import subprocess

from src.globalargs import GlobalArgs
from src.i18n import I18n
from src.options import FSFormats
from src.options import OptionEnum

RED = "\033[0;31m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
ORANGE = "\033[0;33m"
GRAY = "\033[0;37m"
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
    return re.sub('\\s', '', stdout(execute(f'printf "{size}" | numfmt --to=iec', capture_output=True, force=True)))


def from_iec(size: str) -> int:
    """
    The method to convert an iec formatted size in bytes.
    """
    return int(
        re.sub('\\s', '', stdout(execute(f'printf "{size}" | numfmt --from=iec', capture_output=True, force=True))))


def build_partition_name(disk_name: str, index: int) -> str or None:
    """
    A method to build a partition name with a disk and an index.
    :param disk_name:
    :param index:
    :return:
    """
    block_devices_str = stdout(execute('lsblk -J', capture_output=True, force=True))
    if not block_devices_str:
        return None
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
    return prompt_option(_("Which format type do you want ? (%s) : "), _("Format type '%s' is not supported."),
                         FSFormats, _("Supported format types : "), FSFormats.EXT4)


def ask_password(username: str = "root") -> str:
    """
    A method to ask a password to the user.
    :param username:
    :return:
    """
    password_confirm = None
    password = None
    while password is None or password != password_confirm:
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
                execute(f'mkfs.vfat "{partition}"')
            execute(f'mkdir -p "/mnt{mount_point}"')
            execute(f'mount "{partition}" "/mnt{mount_point}"')
        case "btrfs":
            if formatting:
                execute(f'mkfs.btrfs -f "{partition}"')
            execute(f'mkdir -p "/mnt{mount_point}"')
            execute(f'mount -o compress=zstd "{partition}" "/mnt{mount_point}"')
        case _:
            if formatting:
                execute(f'mkfs.ext4 "{partition}"')
            execute(f'mkdir -p "/mnt{mount_point}"')
            execute(f'mount "{partition}" "/mnt{mount_point}"')


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
        execute('clear', force=True)
    print(f'\n{GREEN}{message}{NOCOLOR}')


def print_sub_step(message: str):
    """
    A method to print a sub step message.
    :param message:
    """
    print(f'{CYAN}  * {message}{NOCOLOR}')


def log(message: str):
    """
    A method to print a log message.
    :param message:
    :return:
    """
    if GlobalArgs().test():
        print(f'{GRAY}> {message}{NOCOLOR}')


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


def print_supported(supported_msg: str, options: type(OptionEnum), *ignores: OptionEnum):
    """
    A method to print all supported options.
    :param supported_msg:
    :param options:
    :param ignores:
    :return:
    """
    supported_options = [option for option in list(options) if option not in ignores]
    print_step(supported_msg, clear=False)
    print_sub_step(", ".join(supported_options))
    print('')


def prompt_option(message: str, error_msg: str, options: type(OptionEnum), supported_msg: str or None,
                  default: OptionEnum or None, *ignores: OptionEnum,
                  new_line_prompt: bool = True) -> OptionEnum or None:
    """
    A method to prompt for a bundle.
    :param supported_msg:
    :param message:
    :param error_msg:
    :param options:
    :param default:
    :param new_line_prompt:
    :return:
    """
    readline.set_completer(
        lambda text, state:
        ([option for option in list(options) if not text or option.value.startswith(text)] + [None])[state])
    supported_options = [option for option in list(options) if option not in ignores]
    if supported_msg:
        print_supported(supported_msg, options, *ignores)
    option_ok = False
    option = None
    while not option_ok:
        prompt_message = message
        if default:
            prompt_message = message % default.value
        if new_line_prompt:
            option_name = prompt_ln(
                prompt_message,
                default=default).lower()
        else:
            option_name = prompt(
                prompt_message,
                default=default).lower()
        if option_name in supported_options:
            option_ok = True
            option = options(option_name)
        else:
            print_error(error_msg % option_name, do_pause=False)
            continue
    readline.set_completer(lambda text, state: (glob.glob(text + '*') + [None])[state])
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
    execute('read -n 1 -sr', force=True)
    if end_newline:
        print("")


def execute(command: str, check: bool = True, capture_output: bool = False,
            force: bool = False) -> subprocess.CompletedProcess:
    """
    A method to exec a command.
    :param command:
    :param check:
    :param capture_output:
    :param force:
    :return:
    """
    if force or not GlobalArgs().test():
        log(f"Real execution of: {command}")
        return subprocess.run(command, shell=True, check=check, capture_output=capture_output)
    log(f"Fake execution of: {command}")
    fake_result = subprocess.CompletedProcess(args=command, returncode=0)
    if capture_output:
        fake_result.stdout = b''
    return fake_result


def stdout(process_result: subprocess.CompletedProcess):
    """
    A method to get a decoded stdout.
    :param process_result:
    :return:
    """
    return process_result.stdout.decode(encodings.utf_8.getregentry().name)
