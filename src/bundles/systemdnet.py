"""
The systemd network bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.partitioninginfo import PartitioningInfo
from src.prelaunchinfo import PreLaunchInfo
from src.systeminfo import SystemInfo
from src.utils import print_sub_step, execute

_ = I18n().gettext


class SystemdNet(Bundle):
    """
    Grml ZSH config class.
    """

    def print_resume(self):
        print_sub_step(_("Enable systemd network stack."))

    def configure(self, system_info: SystemInfo, pre_launch_info: PreLaunchInfo, partitioning_info: PartitioningInfo):
        execute('cp -r /etc/systemd/network /mnt/etc/systemd/')
        execute('arch-chroot /mnt bash -c "systemctl enable systemd-networkd"')
        execute('arch-chroot /mnt bash -c "systemctl enable systemd-resolved"')
