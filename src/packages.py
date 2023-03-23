"""
The packages management singleton module
"""
import readline
from threading import Lock

from src.i18n import I18n
from src.utils import prompt_ln, print_error, stdout, execute, glob_completer

_ = I18n().gettext


class PackagesMeta(type):
    """
    Thread-safe implementation of Singleton to store all archlinux packages.
    """

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class Packages(metaclass=PackagesMeta):
    """
    The singleton implementation containing all archlinux packages and autocompleted prompt method.
    """

    packages: set[str]

    def __init__(self) -> None:
        self.packages = set(
            stdout(
                execute(
                    "pacman -Sl | awk '{print $2}'",
                    check=False,
                    force=True,
                    capture_output=True,
                )
            )
            .strip()
            .split("\n")
        )

    def exist(self, package: str) -> bool:
        """
        A method to check if a package exist.
        """
        return package in self.packages

    def ask_packages(self) -> set[str]:
        """
        A method to ask the user for more packages to install.
        """
        readline.set_completer(
            lambda text, state: (
                [
                    package
                    for package in self.packages
                    if (text and package.startswith(text))
                ]
            )[state]
        )

        pkgs_select_ok = False
        more_pkgs = set()
        while not pkgs_select_ok:
            more_pkgs = set()
            more_pkgs_str = prompt_ln(
                _(
                    "Install more packages ? (type extra packages full names, example : 'htop neofetch', "
                    "leave blank if none) : "
                )
            )
            pkgs_select_ok = True
            if more_pkgs_str:
                for pkg in more_pkgs_str.split():
                    if not self.exist(pkg):
                        pkgs_select_ok = False
                        print_error(_("Package %s doesn't exist.") % pkg)
                        break
                    more_pkgs.add(pkg)

        readline.set_completer(glob_completer)
        return more_pkgs
