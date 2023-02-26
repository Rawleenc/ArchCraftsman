"""
The network manager bundle module
"""

from src.bundles.bundle import Bundle
from src.bundles.systemdnet import SystemdNet
from src.i18n import I18n
from src.partitioninginfo import PartitioningInfo
from src.utils import print_sub_step, execute

_ = I18n().gettext


class Iwd(Bundle):
    """
    Grml ZSH config class.
    """

    def packages(self, system_info: dict[str, any]) -> list[str]:
        packages = ["iwd"]
        return packages

    def print_resume(self):
        print_sub_step(_("Install Iwd."))
        SystemdNet(self.name).print_resume()

    def configure(self, system_info, pre_launch_info, partitioning_info: PartitioningInfo):
        execute('arch-chroot /mnt bash -c "systemctl enable iwd.service"')
        SystemdNet(self.name).configure(system_info, pre_launch_info, partitioning_info)
