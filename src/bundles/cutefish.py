"""
The cutefish bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.partitioninginfo import PartitioningInfo
from src.prelaunchinfo import PreLaunchInfo
from src.utils import print_sub_step, prompt_bool, execute

_ = I18n().gettext


class Cutefish(Bundle):
    """
    Bundle class.
    """
    display_manager = True

    def packages(self, system_info) -> list[str]:
        packages = ["cutefish", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa", "pavucontrol"]
        if self.display_manager:
            packages.extend(["sddm"])
        return packages

    def prompt_extra(self):
        self.display_manager = prompt_bool(
            _("The display manager to install is '%s'. Do you want to install it ?") % "SDDM",
            default=True)

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % ("SDDM" if self.display_manager else _("none")))

    def configure(self, system_info, pre_launch_info: PreLaunchInfo, partitioning_info: PartitioningInfo):
        if self.display_manager:
            execute('arch-chroot /mnt bash -c "systemctl enable sddm"')
        pre_launch_info.setup_chroot_keyboard()
