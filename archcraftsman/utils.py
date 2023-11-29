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
The general utility methods and tools module
"""
import importlib.resources
import re
import readline
import subprocess
import typing

import archcraftsman.base
import archcraftsman.i18n
import archcraftsman.options

_ = archcraftsman.i18n.translate


def generate_translations(global_language: str):
    """
    Generate translations for ArchCraftsman.
    """
    locale_file_path = importlib.resources.files("archcraftsman.locales").joinpath(
        f"{global_language}.po"
    )
    if locale_file_path.is_file():
        archcraftsman.base.execute(
            f"msgfmt -o /usr/share/locale/fr/LC_MESSAGES/archcraftsman.mo {locale_file_path} &>/dev/null",
            force=True,
            sudo=True,
        )


def to_iec(size: int) -> str:
    """
    The method to convert a size in iec format.
    """
    return re.sub(
        "\\s",
        "",
        archcraftsman.base.execute(
            f'printf "{size}" | numfmt --to=iec --format="%.0f"',
            capture_output=True,
            force=True,
        ).output,
    )


def from_iec(size: str) -> int:
    """
    The method to convert an iec formatted size in bytes.
    """
    try:
        value = re.sub(
            "\\s",
            "",
            archcraftsman.base.execute(
                f'printf "{size}" | numfmt --from=iec',
                capture_output=True,
                force=True,
            ).output,
        )
        return int(value) if value else 0
    except subprocess.CalledProcessError:
        return 0


def print_supported(supported_msg: str, options: list[str], *ignores: str):
    """
    A method to print all supported options.
    """
    supported_options = [option for option in options if option not in ignores]
    archcraftsman.base.print_step(supported_msg, clear=False)
    archcraftsman.base.print_sub_step(" ".join(supported_options))
    print("")


T = typing.TypeVar("T", bound=archcraftsman.options.OptionEnum)


def prompt_option(
    message: str,
    error_msg: str,
    options: type[T],
    supported_msg: typing.Optional[str],
    default: typing.Optional[T],
    *ignores: T,
    new_line_prompt: bool = True,
) -> typing.Optional[T]:
    """
    A method to prompt for a bundle.
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
        print_supported(supported_msg, list(options), *ignores)
    option_ok = False
    option = None
    while not option_ok:
        prompt_message = message
        if default:
            prompt_message = message % default.value
        if new_line_prompt:
            option_name = archcraftsman.base.prompt_ln(
                prompt_message, default=default
            ).lower()
        else:
            option_name = archcraftsman.base.prompt(
                prompt_message, default=default
            ).lower()
        if option_name in supported_options:
            option_ok = True
            option = options(option_name)
        else:
            archcraftsman.base.print_error(error_msg % option_name, do_pause=False)
    readline.set_completer(archcraftsman.base.glob_completer)
    return option


def ask_keymap(default: str) -> str:
    """
    A method to prompt for a keymap.
    """
    keymaps = (
        archcraftsman.base.execute(
            "localectl list-keymaps",
            capture_output=True,
            force=True,
        )
        .output.strip()
        .split("\n")
    )
    readline.set_completer(
        lambda text, state: (
            [
                option
                for option in keymaps + ["help"]
                if (not text or option.lower().startswith(text.lower()))
            ]
            + [None]
        )[state]
    )
    keymap_ok = False
    keymap = ""
    while not keymap_ok:
        prompt_message = (
            _(
                "Type your installation's keymap, or 'help' to get the list of keymaps (%s) : "
            )
            % default
        )
        keymap = archcraftsman.base.prompt_ln(prompt_message, default=default).lower()
        if keymap == "help":
            archcraftsman.base.print_help(" ".join(keymaps))
            continue
        if keymap in keymaps:
            keymap_ok = True
        else:
            archcraftsman.base.print_error(
                _("Keymap '%s' doesn't exist.") % keymap, do_pause=False
            )
    readline.set_completer(archcraftsman.base.glob_completer)
    return keymap


def ask_format_type(
    part_type: archcraftsman.options.PartTypes = archcraftsman.options.PartTypes.OTHER,
) -> archcraftsman.options.FSFormats:
    """
    The method to ask the user for the format type.
    """
    part_type_info = archcraftsman.options.get_type_info(part_type)
    if part_type_info and len(part_type_info.supported_formats) == 1:
        return part_type_info.supported_formats[0]
    ignores = [
        format_type
        for format_type in archcraftsman.options.FSFormats
        if part_type_info and format_type not in part_type_info.supported_formats
    ]
    format_type = prompt_option(
        _("Which format type do you want ? (%s) : "),
        _("Format type '%s' is not supported."),
        archcraftsman.options.FSFormats,
        _("Supported format types : "),
        archcraftsman.options.FSFormats.BTRFS,
        *ignores,
    )
    return format_type if format_type else archcraftsman.options.FSFormats.BTRFS


def ask_swap_type() -> archcraftsman.options.SwapTypes:
    """
    The method to ask the user for the swap type.
    """
    swap_type = prompt_option(
        _("What type of Swap do you want ? (%s) : "),
        _("Swap type '%s' is not supported."),
        archcraftsman.options.SwapTypes,
        _("Supported Swap types : "),
        archcraftsman.options.SwapTypes.FILE,
    )
    return swap_type if swap_type else archcraftsman.options.SwapTypes.NONE


def ask_encryption_block_name() -> str:
    """
    Method to ask for encryption block name.
    """
    block_name_pattern = re.compile("^[a-z][a-z\\d_]*$")
    block_name_ok = False
    block_name = ""
    while not block_name_ok:
        block_name = archcraftsman.base.prompt_ln(
            _("What will be the encrypted block name ? : "), required=True
        )
        if block_name and not block_name_pattern.match(block_name):
            archcraftsman.base.print_error(_("Invalid encrypted block name."))
            continue
        block_name_ok = True
    return block_name


def ask_password(prompt_message: str, required: bool = False) -> str:
    """
    A method to ask a password to the user.
    """
    password_confirm = None
    password = None
    while password is None or password != password_confirm:
        password = archcraftsman.base.prompt_passwd(prompt_message, required=required)
        password_confirm = archcraftsman.base.prompt_passwd(
            _("Enter it again to confirm : "), required=required
        )
        if password != password_confirm:
            archcraftsman.base.print_error(_("Passwords entered don't match."))
    return password


def ask_drive() -> str:
    """
    A method to prompt for a drive to partition.
    """
    drives = (
        archcraftsman.base.execute(
            "lsblk -lpdno NAME,TYPE | grep disk | awk '{print $1}'",
            capture_output=True,
            force=True,
        )
        .output.strip()
        .split("\n")
    )
    readline.set_completer(
        lambda text, state: (
            [option for option in drives if (not text or option.startswith(text))]
            + [None]
        )[state]
    )
    print_supported(_("Detected drives :"), drives)
    drive_ok = False
    drive = ""
    while not drive_ok:
        prompt_message = _(
            "On which drive should Archlinux be installed ? (type the entire name, for example '/dev/sda') : "
        )
        drive = archcraftsman.base.prompt_ln(prompt_message).lower()
        if drive in drives:
            drive_ok = True
        else:
            archcraftsman.base.print_error(
                _("The target drive '%s' doesn't exist.") % drive, do_pause=False
            )
    readline.set_completer(archcraftsman.base.glob_completer)
    return drive


def prompt_bool(
    message: str, default: bool = True, help_msg: typing.Optional[str] = None
) -> bool:
    """
    A method to prompt for a boolean choice.
    """
    message += " ("
    if default:
        message += f"{_('yes').upper()[0]}/{_('no')[0]}"
    else:
        message += f"{_('yes')[0]}/{_('no').upper()[0]}"
    if help_msg:
        message += "/?"
    message += ") : "
    if not default:
        return (
            archcraftsman.base.prompt(f"{message}", help_msg=help_msg).upper()
            == _("yes").upper()[0]
        )
    return (
        archcraftsman.base.prompt(f"{message}", help_msg=help_msg).upper()
        != _("no").upper()[0]
    )
