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
import subprocess
import typing

import archcraftsman.base
import archcraftsman.basesetup
import archcraftsman.bundles.bundle
import archcraftsman.bundles.utils
import archcraftsman.config
import archcraftsman.i18n
import archcraftsman.manualpart
import archcraftsman.options
import archcraftsman.utils

_ = archcraftsman.i18n.translate


def ask_for_kernel() -> typing.Optional[archcraftsman.bundles.bundle.Bundle]:
    """
    A method to ask for a kernel.
    """
    try:
        return archcraftsman.bundles.utils.prompt_bundle(
            "> ",
            _("Kernel '%s' is not supported."),
            archcraftsman.options.Kernels,
            _("Supported kernels : "),
            None,
            new_line_prompt=False,
        )
    except ValueError:
        return None


def ask_for_desktop() -> typing.Optional[archcraftsman.bundles.bundle.Bundle]:
    """
    A method to ask for a desktop environment.
    """
    try:
        return archcraftsman.bundles.utils.prompt_bundle(
            "> ",
            _("Desktop environment '%s' is not supported."),
            archcraftsman.options.Desktops,
            _("Supported desktop environments : "),
            None,
            new_line_prompt=False,
        )
    except ValueError:
        return None


def ask_for_bundle() -> typing.Optional[archcraftsman.bundles.bundle.Bundle]:
    """
    A method to ask for a bundle.
    """
    try:
        return archcraftsman.bundles.utils.prompt_bundle(
            "> ",
            _("Bundle '%s' is not supported."),
            archcraftsman.options.Bundles,
            _("Available bundles : "),
            None,
            archcraftsman.options.Bundles.COPY_ACM,
            new_line_prompt=False,
        )
    except ValueError:
        return None


def ask_for_shell_bundle() -> typing.Optional[archcraftsman.bundles.bundle.Bundle]:
    """
    A method to ask for a bundle.
    """
    try:
        return archcraftsman.bundles.utils.prompt_bundle(
            "> ",
            _("Shell bundle '%s' is not supported."),
            archcraftsman.options.ShellBundles,
            _("Available shell bundles : "),
            None,
            new_line_prompt=False,
        )
    except ValueError:
        return None


def install_bundle(bundle: archcraftsman.bundles.bundle.Bundle):
    """
    The method to install the bundle.
    """
    if bundle.is_aur():
        bundle.configure()
    else:
        if len(bundle.packages()) > 0:
            archcraftsman.base.execute(
                f'pacman -S {" ".join(bundle.packages())}',
                check=False,
            )


def uninstall_bundle(bundle):
    """
    The method to uninstall the bundle.
    """
    if len(bundle.packages()) > 0:
        archcraftsman.base.execute(
            f'pacman -Rsnc {" ".join(bundle.packages())}',
            check=False,
        )


def shell():
    """
    The shell mode method.
    """
    archcraftsman.base.print_step(_("ArchCraftsman interactive shell mode."))
    archcraftsman.utils.print_supported(
        _("Available commands :"), list(archcraftsman.options.Commands)
    )
    want_exit = False
    while not want_exit:
        try:
            command = archcraftsman.utils.prompt_option(
                "> ",
                _("Command '%s' is not supported."),
                archcraftsman.options.Commands,
                None,
                None,
                new_line_prompt=False,
            )
            bundle = None
            match command:
                case archcraftsman.options.Commands.KERNEL:
                    bundle = ask_for_kernel()
                case archcraftsman.options.Commands.DESKTOP:
                    bundle = ask_for_desktop()
                case archcraftsman.options.Commands.BUNDLE:
                    bundle = ask_for_bundle()
                case archcraftsman.options.Commands.SHELL_BUNDLE:
                    bundle = ask_for_shell_bundle()
                case archcraftsman.options.Commands.HELP:
                    archcraftsman.utils.print_supported(
                        _("Available commands :"), list(archcraftsman.options.Commands)
                    )
                    continue
                case archcraftsman.options.Commands.EXIT:
                    want_exit = True
                    archcraftsman.config.serialize()
                    continue

            if (
                bundle
                and bundle.name == archcraftsman.options.ShellBundles.GENERATE_CONFIG
            ):
                archcraftsman.basesetup.pre_launch()
                archcraftsman.basesetup.setup_system()
                partitioning_info_ok: bool = False
                while not partitioning_info_ok:
                    partitioning_info_ok = archcraftsman.manualpart.manual_partitioning(
                        change_disks=False
                    )
                continue

            sub_command = archcraftsman.utils.prompt_option(
                "> ",
                _("Sub-command '%s' is not supported."),
                archcraftsman.options.SubCommands,
                _("Available sub-commands : "),
                None,
                new_line_prompt=False,
            )

            match sub_command:
                case archcraftsman.options.SubCommands.INSTALL:
                    if bundle:
                        install_bundle(bundle)
                case archcraftsman.options.SubCommands.UNINSTALL:
                    if bundle:
                        uninstall_bundle(bundle)
                case archcraftsman.options.SubCommands.CANCEL:
                    continue
        except KeyboardInterrupt:
            archcraftsman.config.serialize()
            archcraftsman.base.print_error(
                _("Script execution interrupted by the user !"), do_pause=False
            )
            want_exit = True
        except subprocess.CalledProcessError as sub_process_exception:
            archcraftsman.config.serialize()
            archcraftsman.base.print_error(
                _("A subprocess execution failed ! See the following error: %s")
                % sub_process_exception,
                do_pause=False,
            )
            want_exit = True
        except EOFError:
            archcraftsman.config.serialize()
            want_exit = True
