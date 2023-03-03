"""
The cups bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.partitioninginfo import PartitioningInfo
from src.prelaunchinfo import PreLaunchInfo
from src.systeminfo import SystemInfo
from src.utils import print_sub_step, execute

_ = I18n().gettext


class Cups(Bundle):
    """
    Cups class.
    """

    def packages(self, system_info: SystemInfo) -> list[str]:
        return ["cups", "cups-pdf", "avahi", "samba", "foomatic-db-engine", "foomatic-db", "foomatic-db-ppds",
                "foomatic-db-nonfree-ppds", "foomatic-db-gutenprint-ppds", "gutenprint", "ghostscript"]

    def print_resume(self):
        print_sub_step(_("Install Cups."))

    def configure(self, system_info: SystemInfo, pre_launch_info: PreLaunchInfo, partitioning_info: PartitioningInfo):
        execute('arch-chroot /mnt bash -c "systemctl enable avahi-daemon"')
        execute('arch-chroot /mnt bash -c "systemctl enable cups"')
        execute('arch-chroot /mnt bash -c "systemctl enable cups-browsed"')
