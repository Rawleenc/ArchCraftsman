"""
The general utility methods and tools module
"""
import encodings
import getpass
import glob
import os
import re
import readline
import subprocess
from typing import Optional

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


def glob_completer(text, state) -> str:
    """
    The glob completer for readline completions.
    :param text:
    :param state:
    :return:
    """
    return [
        path + "/" if os.path.isdir(path) else path for path in glob.glob(text + "*")
    ][state]


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
    return re.sub(
        "\\s",
        "",
        stdout(
            execute(
                f'printf "{size}" | numfmt --to=iec', capture_output=True, force=True
            )
        ),
    )


def from_iec(size: str) -> int:
    """
    The method to convert an iec formatted size in bytes.
    """
    return int(
        re.sub(
            "\\s",
            "",
            stdout(
                execute(
                    f'printf "{size}" | numfmt --from=iec',
                    capture_output=True,
                    force=True,
                )
            ),
        )
    )


def ask_format_type() -> Optional[FSFormats]:
    """
    The method to ask the user for the format type.
    :return:
    """
    return FSFormats(
        prompt_option(
            _("Which format type do you want ? (%s) : "),
            _("Format type '%s' is not supported."),
            FSFormats,
            _("Supported format types : "),
            FSFormats.EXT4,
            FSFormats.VFAT,
        )
    )


def ask_encryption_block_name() -> Optional[str]:
    """
    Method to ask for encryption block name.
    :return:
    """
    block_name_pattern = re.compile("^[a-z][a-z\\d_]*$")
    block_name_ok = False
    block_name = None
    while not block_name_ok:
        block_name = prompt_ln(
            _("What will be the encrypted block name ? : "), required=True
        )
        if block_name and not block_name_pattern.match(block_name):
            print_error(_("Invalid encrypted block name."))
            continue
        block_name_ok = True
    return block_name


def ask_password(prompt_message: str, required: bool = False) -> str:
    """
    A method to ask a password to the user.
    :param prompt_message:
    :param required:
    :return:
    """
    password_confirm = None
    password = None
    while password is None or password != password_confirm:
        password = prompt_passwd(prompt_message, required=required)
        password_confirm = prompt_passwd(
            _("Enter it again to confirm : "), required=required
        )
        if password != password_confirm:
            print_error(_("Passwords entered don't match."))
    return password


def print_error(message: str, do_pause: bool = True):
    """
    A method to print an error.
    :param message:
    :param do_pause:
    :return:
    """
    print(f"\n{RED}  /!\\ {message}{NOCOLOR}\n")
    if do_pause:
        pause(end_newline=True)


def print_step(message: str, clear: bool = True):
    """
    A method to print a step message.
    :param message:
    :param clear:
    """
    if clear:
        execute("clear", force=True)
    print(f"\n{GREEN}{message}{NOCOLOR}")


def print_sub_step(message: str):
    """
    A method to print a sub step message.
    :param message:
    """
    print(f"{CYAN}  * {message}{NOCOLOR}")


def log(message: str):
    """
    A method to print a log message.
    :param message:
    :return:
    """
    if GlobalArgs().test():
        print(f"{GRAY}> {message}{NOCOLOR}")


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


def input_str(message: str, password: bool = False) -> str:
    """
    A method to ask to input something.
    :param message:
    :param password:
    :return:
    """
    if password:
        return getpass.getpass(prompt=f"{ORANGE}{message}{NOCOLOR}")
    return input(f"{ORANGE}{message}{NOCOLOR}")


def prompt(
    message: str,
    default: Optional[str] = None,
    help_msg: Optional[str] = None,
    required: bool = False,
    password: bool = False,
) -> str:
    """
    A method to prompt for a user input.
    :param message:
    :param default:
    :param help_msg:
    :param required:
    :param password:
    :return:
    """
    user_input_ok = False
    user_input = ""
    while not user_input_ok:
        user_input = input_str(f"{ORANGE}{message}{NOCOLOR}", password=password)
        if user_input == "?" and help_msg:
            print_help(help_msg)
            continue
        if not user_input and default:
            user_input = default
        if required and (user_input is None or not user_input):
            print_error(_("The input must not be empty."))
            continue
        user_input_ok = True
    return user_input


def prompt_ln(
    message: str,
    default: Optional[str] = None,
    help_msg: Optional[str] = None,
    required: bool = False,
) -> str:
    """
    A method to prompt for a user input with a new line for the user input.
    :param message:
    :param default:
    :param help_msg:
    :param required:
    :return:
    """
    return prompt(
        f"{message}\n> ", default=default, help_msg=help_msg, required=required
    )


def print_supported(
    supported_msg: str, options: type[OptionEnum], *ignores: OptionEnum
):
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
    print("")


def prompt_option(
    message: str,
    error_msg: str,
    options: type[OptionEnum],
    supported_msg: Optional[str],
    default: Optional[OptionEnum],
    *ignores: OptionEnum,
    new_line_prompt: bool = True,
) -> Optional[OptionEnum]:
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
        lambda text, state: (
            [
                option
                for option in list(options)
                if (not text or option.value.startswith(text)) and option not in ignores
            ]
            + [None]
        )[state]
    )
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
            option_name = prompt_ln(prompt_message, default=default).lower()
        else:
            option_name = prompt(prompt_message, default=default).lower()
        if option_name in supported_options:
            option_ok = True
            option = options(option_name)
        else:
            print_error(error_msg % option_name, do_pause=False)
            continue
    readline.set_completer(glob_completer)
    return option


def prompt_bool(
    message: str, default: bool = True, help_msg: Optional[str] = None
) -> bool:
    """
    A method to prompt for a boolean choice.
    :param message:
    :param default:
    :param help_msg:
    :return:
    """
    message += " ("
    if default:
        message += f"{_('yes').upper()[0]}/{_('no')[0]}"
    else:
        message += f"{_('yes')[0]}/{_('no').upper()[0]}"
    if help_msg is not None:
        message += "/?"
    message += ") : "
    if not default:
        return prompt(f"{message}", help_msg=help_msg).upper() == _("yes").upper()[0]
    return prompt(f"{message}", help_msg=help_msg).upper() != _("no").upper()[0]


def prompt_passwd(message: str, required: bool = False):
    """
    A method to prompt for a password without displaying an echo.
    :param message:
    :param required:
    :return:
    """
    return prompt(f"{ORANGE}{message}{NOCOLOR}", required=required, password=True)


def pause(start_newline: bool = False, end_newline: bool = False):
    """
    A method to insert a one key press pause.
    :param start_newline:
    :param end_newline:
    """
    message = _("Press any key to continue...")
    if start_newline:
        print("")
    print(f"{ORANGE}{message}{NOCOLOR}")
    execute("read -n 1 -sr", force=True)
    if end_newline:
        print("")


def execute(
    command: str, check: bool = True, capture_output: bool = False, force: bool = False
) -> subprocess.CompletedProcess:
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
        return subprocess.run(
            command, shell=True, check=check, capture_output=capture_output
        )
    log(f"Fake execution of: {command}")
    fake_result = subprocess.CompletedProcess(args=command, returncode=0)
    if capture_output:
        fake_result.stdout = b""
    return fake_result


def stdout(process_result: subprocess.CompletedProcess) -> str:
    """
    A method to get a decoded stdout.
    :param process_result:
    :return:
    """
    return process_result.stdout.decode(encodings.utf_8.getregentry().name)
