"""
The yay bundle module
"""

from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import I18n
from archcraftsman.utils import execute, print_sub_step


_ = I18n().gettext


class Yay(Bundle):
    """
    The Yay class.
    """

    def packages(self, system_info) -> list[str]:
        return ["yay"]

    def is_aur(self) -> bool:
        return True

    def print_resume(self):
        print_sub_step(_("Install YAY."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        execute("git clone https://aur.archlinux.org/yay")
        execute("cd yay && makepkg -si && cd - && rm -rf yay")
