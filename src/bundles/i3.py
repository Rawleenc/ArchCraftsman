"""
The i3 bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.partitioninginfo import PartitioningInfo
from src.prelaunchinfo import PreLaunchInfo
from src.utils import print_sub_step, execute

_ = I18n().gettext


class I3(Bundle):
    """
    Bundle class.
    """

    def packages(self, system_info) -> list[str]:
        packages = ["i3", "rofi", "dmenu", "perl", "alacritty", "xorg-server", "xorg-xinit", "alsa-utils", "pulseaudio",
                    "pulseaudio-alsa", "pavucontrol", "system-config-printer", "acpid",
                    "gnome-keyring", "dex"]
        return packages

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % _("none"))

    def configure(self, system_info, pre_launch_info: PreLaunchInfo, partitioning_info: PartitioningInfo):
        execute('arch-chroot /mnt bash -c "systemctl enable acpid"')
        pre_launch_info.setup_chroot_keyboard()
