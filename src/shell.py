"""
The shell mode module
"""
from subprocess import CalledProcessError

from src.bundles.utils import prompt_bundle
from src.i18n import I18n
from src.options import Commands, Kernels, Desktops, Bundles, SubCommands
from src.utils import prompt_option, print_error, print_supported, execute, print_step

_ = I18n().gettext


def ask_for_kernel() -> str:
    """
    A method to ask for a kernel.
    :return:
    """
    kernel = prompt_bundle("> ", _("Kernel '%s' is not supported."), Kernels, _("Supported kernels : "), None,
                           new_line_prompt=False)
    return " ".join(kernel.packages({}))


def ask_for_desktop() -> str:
    """
    A method to ask for a desktop environment.
    :return:
    """
    desktop = prompt_bundle("> ", _("Desktop environment '%s' is not supported."), Desktops,
                            _("Supported desktop environments : "), None, new_line_prompt=False)
    return " ".join(desktop.packages({}))


def ask_for_bundle() -> str:
    """
    A method to ask for a bundle.
    :return:
    """
    bundle = prompt_bundle("> ", _("Bundle '%s' is not supported."), Bundles, _("Available bundles : "), None,
                           new_line_prompt=False)
    if bundle:
        return " ".join(bundle.packages({}))
    return ""


def shell():
    """
    The shell mode method.
    :return:
    """
    print_step(_("ArchCraftsman interactive shell mode."))
    print_supported(_("Available commands :"), Commands)
    want_exit = False
    while not want_exit:
        try:
            command = prompt_option("> ", _("Command '%s' is not supported."), Commands, None, None,
                                    new_line_prompt=False)
            packages = None
            match command:
                case Commands.KERNEL:
                    packages = ask_for_kernel()
                case Commands.DESKTOP:
                    packages = ask_for_desktop()
                case Commands.BUNDLE:
                    packages = ask_for_bundle()
                case Commands.HELP:
                    print_supported(_("Available commands :"), Commands)
                    continue
                case Commands.EXIT:
                    want_exit = True
                    continue

            sub_command = prompt_option("> ", _("Sub-command '%s' is not supported."), SubCommands,
                                        _("Available sub-commands : "), None, new_line_prompt=False)
            match sub_command:
                case SubCommands.INSTALL:
                    execute(f"pacman -S {packages}", check=False)
                case SubCommands.UNINSTALL:
                    execute(f"pacman -Rsnc {packages}", check=False)
        except KeyboardInterrupt:
            print_error(_("Script execution interrupted by the user !"), do_pause=False)
            want_exit = True
        except CalledProcessError as sub_process_exception:
            print_error(_("A subprocess execution failed ! See the following error: %s") % sub_process_exception,
                        do_pause=False)
            want_exit = True
        except EOFError:
            want_exit = True
