"""
The shell mode module
"""
from subprocess import CalledProcessError
from typing import Optional

from src.bundles.bundle import Bundle
from src.bundles.utils import prompt_bundle
from src.i18n import I18n
from src.options import Commands, Kernels, Desktops, Bundles, SubCommands
from src.utils import prompt_option, print_error, print_supported, execute, print_step

_ = I18n().gettext


def ask_for_kernel() -> Optional[Bundle]:
    """
    A method to ask for a kernel.
    """
    try:
        return prompt_bundle(
            "> ",
            _("Kernel '%s' is not supported."),
            Kernels,
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
            _("Available bundles : "),
            None,
            Bundles.COPY_ACM,
            new_line_prompt=False,
        )
    except ValueError:
        return None


def install_bundle(bundle):
    """
    The method to install the bundle.
    """
    match bundle.name:
        case _:
            if len(bundle.packages({})) > 0:
                execute(f'pacman -S {" ".join(bundle.packages({}))}', check=False)


def uninstall_bundle(bundle):
    """
    The method to uninstall the bundle.
    """
    match bundle.name:
        case _:
            if len(bundle.packages({})) > 0:
                execute(f'pacman -Rsnc {" ".join(bundle.packages({}))}', check=False)


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
                case Commands.HELP:
                    print_supported(_("Available commands :"), list(Commands))
                    continue
                case Commands.EXIT:
                    want_exit = True
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
        except KeyboardInterrupt:
            print_error(_("Script execution interrupted by the user !"), do_pause=False)
            want_exit = True
        except CalledProcessError as sub_process_exception:
            print_error(
                _("A subprocess execution failed ! See the following error: %s")
                % sub_process_exception,
                do_pause=False,
            )
            want_exit = True
        except EOFError:
            want_exit = True
