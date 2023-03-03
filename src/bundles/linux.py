"""
All supported linux kernel bundles module
"""
from src.bundles import bundle
from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.systeminfo import SystemInfo
from src.utils import print_sub_step

_ = I18n().gettext


class LinuxCurrent(bundle.Bundle):
    """
    The Linux current kernel class.
    """

    def packages(self, system_info: SystemInfo) -> list[str]:
        return ["linux", "linux-headers"]

    def print_resume(self):
        print_sub_step(_("Install Linux current kernel."))


class LinuxHardened(Bundle):
    """
    The Linux hardened kernel class.
    """

    def packages(self, system_info: SystemInfo) -> list[str]:
        return ["linux-hardened", "linux-hardened-headers"]

    def print_resume(self):
        print_sub_step(_("Install Linux hardened kernel."))


class LinuxLts(bundle.Bundle):
    """
    The Linux LTS kernel class.
    """

    def packages(self, system_info: SystemInfo) -> list[str]:
        return ["linux-lts", "linux-lts-headers"]

    def print_resume(self):
        print_sub_step(_("Install Linux LTS kernel."))


class LinuxZen(bundle.Bundle):
    """
    The Linux zen kernel class.
    """

    def packages(self, system_info: SystemInfo) -> list[str]:
        return ["linux-zen", "linux-zen-headers"]

    def print_resume(self):
        print_sub_step(_("Install Linux zen kernel."))
