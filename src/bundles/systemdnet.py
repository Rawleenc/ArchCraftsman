"""
The systemd network bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.partitioninginfo import PartitioningInfo
from src.utils import print_sub_step, execute

_ = I18n().gettext


class SystemdNet(Bundle):
    """
    Grml ZSH config class.
    """

    def print_resume(self):
        print_sub_step(_("Enable systemd network stack."))

    def configure(self, system_info, pre_launch_info, partitioning_info: PartitioningInfo):
        execute('arch-chroot /mnt bash -c "systemd-networkd.service"')
        execute('arch-chroot /mnt bash -c "systemd-resolved.service"')
