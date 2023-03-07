"""
The plasma bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.options import Bundles
from src.partitioninginfo import PartitioningInfo
from src.prelaunchinfo import PreLaunchInfo
from src.systeminfo import SystemInfo
from src.utils import print_sub_step, prompt_bool, execute

_ = I18n().gettext


class Plasma(Bundle):
    """
    Bundle class.
    """
    minimal = False
    plasma_wayland = False

    def packages(self, system_info: SystemInfo) -> list[str]:
        packages = ["plasma", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa",
                    "xdg-desktop-portal", "xdg-desktop-portal-kde"]
        if self.plasma_wayland:
            packages.extend(["plasma-wayland-session", "qt5-wayland"])
            if system_info.bundles and Bundles.NVIDIA in [bundle.name for bundle in system_info.bundles]:
                packages.append("egl-wayland")
            if self.minimal is not True:
                packages.append("kde-applications")
        return packages

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % "SDDM")
        if self.minimal:
            print_sub_step(_("Install a minimal environment."))
        if self.plasma_wayland:
            print_sub_step(_("Install Wayland support for the plasma session."))

    def prompt_extra(self):
        self.minimal = prompt_bool(
            _("Install a minimal environment ?"),
            default=False,
            help_msg=_("If yes, the script will not install any extra packages, only base packages."))
        self.plasma_wayland = prompt_bool(_("Install Wayland support for the plasma session ?"),
                                          default=False)

    def configure(self, system_info: SystemInfo, pre_launch_info: PreLaunchInfo, partitioning_info: PartitioningInfo):
        execute('arch-chroot /mnt bash -c "systemctl enable sddm"')
        pre_launch_info.setup_chroot_keyboard()
