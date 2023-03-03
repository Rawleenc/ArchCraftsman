"""
The systemd network bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.partitioninginfo import PartitioningInfo
from src.prelaunchinfo import PreLaunchInfo
from src.utils import print_sub_step, execute, log

_ = I18n().gettext


class SystemdNet(Bundle):
    """
    Grml ZSH config class.
    """

    def print_resume(self):
        print_sub_step(_("Enable systemd network stack."))

    def configure(self, system_info, pre_launch_info: PreLaunchInfo, partitioning_info: PartitioningInfo):
        content = [
            "[Match]\n",
            "Name=*\n\n",
            "[Network]\n",
            "DHCP=yes\n"
        ]
        try:
            with open("/mnt/etc/systemd/network/20-wired.network", "w", encoding="UTF-8") as systemd_net_config_file:
                systemd_net_config_file.writelines(content)
        except FileNotFoundError as exception:
            log(f"Exception: {exception}")
        execute('arch-chroot /mnt bash -c "systemctl enable systemd-networkd"')
        execute('arch-chroot /mnt bash -c "systemctl enable systemd-resolved"')
