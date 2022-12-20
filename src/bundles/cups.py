import os

from src.archcraftsman import _
from src.bundles.bundle import Bundle
from src.utils import print_sub_step


class Cups(Bundle):
    """
    Cups class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["cups", "cups-pdf", "avahi", "samba", "foomatic-db-engine", "foomatic-db", "foomatic-db-ppds",
                "foomatic-db-nonfree-ppds", "foomatic-db-gutenprint-ppds", "gutenprint", "ghostscript"]

    def print_resume(self):
        print_sub_step(_("Install Cups."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        os.system('arch-chroot /mnt bash -c "systemctl enable avahi-daemon"')
        os.system('arch-chroot /mnt bash -c "systemctl enable cups"')
        os.system('arch-chroot /mnt bash -c "systemctl enable cups-browsed"')
