"""
The main file systems bundle module
"""
from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.systeminfo import SystemInfo
from src.utils import print_sub_step

_ = I18n().gettext


def get_main_file_systems() -> list[str]:
    """
    The method to get the package list of the main file systems group.
    :return:
    """
    return [
        "btrfs-progs",
        "dosfstools",
        "exfatprogs",
        "f2fs-tools",
        "e2fsprogs",
        "jfsutils",
        "nilfs-utils",
        "ntfs-3g",
        "reiserfsprogs",
        "udftools",
        "xfsprogs",
    ]


class MainFileSystems(Bundle):
    """
    The main file systems class.
    """

    def packages(self, system_info: SystemInfo) -> list[str]:
        return get_main_file_systems()

    def print_resume(self):
        print_sub_step(_("Install main file systems support."))
