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
The shell mode module
"""
from subprocess import CalledProcessError
from typing import Optional

from archcraftsman import config
from archcraftsman.base import execute, print_error, print_step
from archcraftsman.basesetup import pre_launch, setup_system
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.bundles.utils import prompt_bundle
from archcraftsman.i18n import _
from archcraftsman.manualpart import manual_partitioning
from archcraftsman.options import (
    Bundles,
    BundleTypes,
    Commands,
    Desktops,
    Kernels,
    ShellBundles,
    SubCommands,
)
from archcraftsman.utils import print_supported, prompt_option


def ask_for_kernel() -> Optional[Bundle]:
    """
    A method to ask for a kernel.
    """
    try:
        return prompt_bundle(
            "> ",
            _("Kernel '%s' is not supported."),
            Kernels,
            BundleTypes.KERNEL,
            _("Supported kernels : "),
            None,
            new_line_prompt=False,
        )
    except ValueError:
        return None


def ask_for_desktop() -> Optional[Bundle]:
    """
    A method to ask for a desktop environment.
    """
    try:
        return prompt_bundle(
            "> ",
            _("Desktop environment '%s' is not supported."),
            Desktops,
            BundleTypes.DESKTOP,
            _("Supported desktop environments : "),
            None,
            new_line_prompt=False,
        )
    except ValueError:
        return None


def ask_for_bundle() -> Optional[Bundle]:
    """
    A method to ask for a bundle.
    """
    try:
        return prompt_bundle(
            "> ",
            _("Bundle '%s' is not supported."),
            Bundles,
            BundleTypes.OTHER,
            _("Available bundles : "),
            None,
            Bundles.COPY_ACM,
            new_line_prompt=False,
        )
    except ValueError:
        return None


def ask_for_shell_bundle() -> Optional[Bundle]:
    """
    A method to ask for a bundle.
    """
    try:
        return prompt_bundle(
            "> ",
            _("Shell bundle '%s' is not supported."),
            ShellBundles,
            BundleTypes.OTHER,
            _("Available shell bundles : "),
            None,
            new_line_prompt=False,
        )
    except ValueError:
        return None


def install_bundle(bundle: Bundle):
    """
    The method to install the bundle.
    """
    if bundle.is_aur():
        bundle.configure()
    else:
        if len(bundle.packages()) > 0:
            execute(
                f'pacman -S {" ".join(bundle.packages())}',
                check=False,
            )


def uninstall_bundle(bundle):
    """
    The method to uninstall the bundle.
    """
    if len(bundle.packages()) > 0:
        execute(
            f'pacman -Rsnc {" ".join(bundle.packages())}',
            check=False,
        )


def shell():
    """
    The shell mode method.
    """
    print_step(_("ArchCraftsman interactive shell mode."))
    print_supported(_("Available commands :"), list(Commands))
    want_exit = False
    while not want_exit:
        try:
            command = prompt_option(
                "> ",
                _("Command '%s' is not supported."),
                Commands,
                None,
                None,
                new_line_prompt=False,
            )
            bundle = None
            match command:
                case Commands.KERNEL:
                    bundle = ask_for_kernel()
                case Commands.DESKTOP:
                    bundle = ask_for_desktop()
                case Commands.BUNDLE:
                    bundle = ask_for_bundle()
                case Commands.SHELL_BUNDLE:
                    bundle = ask_for_shell_bundle()
                case Commands.HELP:
                    print_supported(_("Available commands :"), list(Commands))
                    continue
                case Commands.EXIT:
                    want_exit = True
                    config.serialize()
                    continue

            if bundle and bundle.name == ShellBundles.GENERATE_CONFIG:
                pre_launch()
                setup_system()
                partitioning_info_ok: bool = False
                while not partitioning_info_ok:
                    partitioning_info_ok = manual_partitioning(change_disks=False)
                continue

            sub_command = prompt_option(
                "> ",
                _("Sub-command '%s' is not supported."),
                SubCommands,
                _("Available sub-commands : "),
                None,
                new_line_prompt=False,
            )

            match sub_command:
                case SubCommands.INSTALL:
                    if bundle:
                        install_bundle(bundle)
                case SubCommands.UNINSTALL:
                    if bundle:
                        uninstall_bundle(bundle)
                case SubCommands.CANCEL:
                    continue
        except KeyboardInterrupt:
            config.serialize()
            print_error(_("Script execution interrupted by the user !"), do_pause=False)
            want_exit = True
        except CalledProcessError as sub_process_exception:
            config.serialize()
            print_error(
                _("A subprocess execution failed ! See the following error: %s")
                % sub_process_exception,
                do_pause=False,
            )
            want_exit = True
        except EOFError:
            config.serialize()
            want_exit = True
