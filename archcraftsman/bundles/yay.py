"""
The yay bundle module
"""

from archcraftsman.base import execute, is_root, print_error, print_sub_step
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import I18n


_ = I18n().gettext


class Yay(Bundle):
    """
    The Yay class.
    """

    def packages(self) -> list[str]:
        return ["yay"]

    def is_aur(self) -> bool:
        return True

    def print_resume(self):
        print_sub_step(_("Install YAY."))

    def configure(self):
        if is_root():
            print_error(_("You must not be root to install yay."), do_pause=False)
            return
        execute("git clone https://aur.archlinux.org/yay")
        execute("cd yay; makepkg -si; cd -; rm -rf yay")
