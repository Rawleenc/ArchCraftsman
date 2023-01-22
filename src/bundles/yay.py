"""
The yay bundle module
"""
from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.utils import print_sub_step, execute

_ = I18n().gettext


class Yay(Bundle):
    """
    The Yay class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["yay"]

    def print_resume(self):
        print_sub_step(_("Install YAY."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        execute("git clone https://aur.archlinux.org/yay")
        execute("cd yay")
        execute("makepkg -si")
        execute("cd -")
        execute("rm -rf yay")
