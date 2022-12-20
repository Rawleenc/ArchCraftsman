from src.archcraftsman import _
from src.bundles.bundle import Bundle
from src.utils import print_sub_step


def get_main_file_systems() -> [str]:
    """
    The method to get the package list of the main file systems group.
    :return:
    """
    return ["btrfs-progs", "dosfstools", "exfatprogs", "f2fs-tools", "e2fsprogs", "jfsutils", "nilfs-utils",
            "ntfs-3g", "reiserfsprogs", "udftools", "xfsprogs"]


class MainFileSystems(Bundle):
    """
    The main file systems class.
    """

    def packages(self, system_info: {}) -> [str]:
        return get_main_file_systems()

    def print_resume(self):
        print_sub_step(_("Install main file systems support."))
