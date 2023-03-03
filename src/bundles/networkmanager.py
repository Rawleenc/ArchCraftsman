"""
The network manager bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.options import Desktops
from src.partitioninginfo import PartitioningInfo
from src.prelaunchinfo import PreLaunchInfo
from src.systeminfo import SystemInfo
from src.utils import print_sub_step, execute

_ = I18n().gettext


class NetworkManager(Bundle):
    """
    Grml ZSH config class.
    """

    def packages(self, system_info: SystemInfo) -> list[str]:
        packages = ["networkmanager"]
        if system_info.desktop and system_info.desktop.name in [Desktops.BUDGIE, Desktops.I3, Desktops.LXQT,
                                                                Desktops.MATE, Desktops.SWAY,
                                                                Desktops.ENLIGHTENMENT, Desktops.XFCE]:
            packages.append("network-manager-applet")
        return packages

    def print_resume(self):
        print_sub_step(_("Install NetworkManager."))

    def configure(self, system_info: SystemInfo, pre_launch_info: PreLaunchInfo, partitioning_info: PartitioningInfo):
        execute('arch-chroot /mnt bash -c "systemctl enable NetworkManager"')
