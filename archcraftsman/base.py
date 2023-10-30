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
The base utility module.
"""
import encodings
import getpass
import glob
import os
import subprocess
import typing

import archcraftsman.arguments
import archcraftsman.i18n

_ = archcraftsman.i18n.translate

RED = "\033[0;31m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
ORANGE = "\033[0;33m"
GRAY = "\033[0;37m"
NOCOLOR = "\033[0m"


def glob_completer(text, state) -> str:
    """
    The glob completer for readline completions.
    """
    return [
        path + "/" if os.path.isdir(path) else path for path in glob.glob(text + "*")
    ][state]


def is_bios() -> bool:
    """
    Check if live system run on a bios.
    """
    return not os.path.exists("/sys/firmware/efi")


def elevate() -> bool:
    """
    A method to elevate the current user to root.
    """
    if is_root():
        return True
    if sudo_exist():
        execute("sudo -v", force=True)
        return True
    return False


def sudo_exist() -> bool:
    """
    A method to check if sudo is installed.
    """
    return execute("which sudo", force=True, capture_output=True).returncode == 0


def is_root() -> bool:
    """
    A method to check if the user is root.
    """
    user = execute("whoami", force=True, capture_output=True).output
    return user.strip() == "root"


class ExecutionResult:
    """
    A class to manage the result of an execution.
    """

    def __init__(self, command: str, result: subprocess.CompletedProcess):
        self.command = command
        self.output = (
            ""
            if not result.stdout
            else result.stdout.decode(encodings.utf_8.getregentry().name)
        )
        self.returncode = result.returncode

    def __bool__(self):
        return self.returncode == 0

    def __str__(self):
        return self.output

    def __repr__(self):
        return self.output

    def __eq__(self, other):
        return (
            self.command == other.command
            and self.returncode == other.returncode
            and self.output == other.output
        )

    def __ne__(self, other):
        return (
            self.command != other.command
            or self.returncode != other.returncode
            or self.output != other.output
        )

    def __hash__(self):
        return hash(self.command) ^ hash(self.returncode) ^ hash(self.output)


def execute(
    command: str,
    check: bool = True,
    capture_output: bool = False,
    force: bool = False,
    chroot: bool = False,
    sudo: bool = False,
) -> ExecutionResult:
    """
    A method to exec a command.
    """
    if force or not archcraftsman.arguments.test():
        if sudo and not sudo_exist() and not is_root():
            raise PermissionError("This script must be run as root.")
        if sudo and sudo_exist() and not is_root():
            command = f"sudo {command}"

        if chroot:
            command = f"arch-chroot /mnt /bin/bash <<END\n{command.strip()}\nEND"

        return ExecutionResult(
            command,
            subprocess.run(
                command, shell=True, check=check, capture_output=capture_output
            ),
        )
    log(
        f"{'(chroot) ' if chroot else ''}"
        f"{'(sudo) ' if sudo else ''}"
        f"Fake execution of: {command}"
    )
    return ExecutionResult(
        command, subprocess.CompletedProcess(args=command, returncode=0, stdout=b"")
    )


def pause(start_newline: bool = False, end_newline: bool = False):
    """
    A method to insert a one key press pause.
    """
    message = _("Press any key to continue...")
    if start_newline:
        print("")
    print(f"{ORANGE}{message}{NOCOLOR}")
    execute("read -n 1 -sr", force=True)
    if end_newline:
        print("")


def print_error(message: str, do_pause: bool = True):
    """
    A method to print an error.
    """
    print(f"\n{RED}  /!\\ {message}{NOCOLOR}\n")
    if do_pause:
        pause(end_newline=True)


def print_step(message: str, clear: bool = True):
    """
    A method to print a step message.
    """
    if clear:
        execute("clear", force=True)
    print(f"\n{GREEN}{message}{NOCOLOR}")


def print_sub_step(message: str):
    """
    A method to print a sub step message.
    """
    print(f"{CYAN}  * {message}{NOCOLOR}")


def log(message: str):
    """
    A method to print a log message.
    """
    if archcraftsman.arguments.test():
        print(f"{GRAY}> {message}{NOCOLOR}")


def print_help(message: str, do_pause: bool = False):
    """
    A method to print an help message.
    """
    print_step(_("Help :"), clear=False)
    print_sub_step(message)
    if do_pause:
        pause(end_newline=True)


def input_str(message: str, password: bool = False) -> str:
    """
    A method to ask to input something.
    """
    if password:
        return getpass.getpass(prompt=f"{ORANGE}{message}{NOCOLOR}")
    return input(f"{ORANGE}{message}{NOCOLOR}")


def prompt(
    message: str,
    default: typing.Optional[str] = None,
    help_msg: typing.Optional[str] = None,
    required: bool = False,
    password: bool = False,
) -> str:
    """
    A method to prompt for a user input.
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
    default: typing.Optional[str] = None,
    help_msg: typing.Optional[str] = None,
    required: bool = False,
) -> str:
    """
    A method to prompt for a user input with a new line for the user input.
    """
    return prompt(
        f"{message}\n> ", default=default, help_msg=help_msg, required=required
    )


def prompt_passwd(message: str, required: bool = False):
    """
    A method to prompt for a password without displaying an echo.
    """
    return prompt(f"{ORANGE}{message}{NOCOLOR}", required=required, password=True)


def update_mirrors():
    """
    A method to update the mirrors.
    """
    ipv6_state: str = execute(
        "cat /sys/module/ipv6/parameters/disable", capture_output=True
    ).output
    options = ["--verbose", "-phttps", "--score 30", "--sort rate", "-a48"]
    if ipv6_state and ipv6_state.strip() == "0":
        options.append("--ipv6")
    execute(f"reflector {' '.join(options)} --save /etc/pacman.d/mirrorlist")
