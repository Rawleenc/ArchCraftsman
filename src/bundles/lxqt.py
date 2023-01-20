"""
The lxqt bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.localesetup import setup_chroot_keyboard
from src.utils import print_sub_step, prompt_bool, execute

_ = I18n().gettext


class Lxqt(Bundle):
    """
    Bundle class.
    """
    display_manager = True

    def packages(self, system_info) -> [str]:
        packages = ["lxqt", "xorg-server", "breeze-icons", "xdg-utils", "xscreensaver", "xautolock", "libpulse",
                    "alsa-lib", "libstatgrab", "libsysstat", "lm_sensors", "system-config-printer", "alsa-utils",
                    "pulseaudio", "pulseaudio-alsa", "pavucontrol", "network-manager-applet"]
        if self.display_manager:
            packages.extend(["sddm"])
        return packages

    def prompt_extra(self):
        self.display_manager = prompt_bool(
            _("The display manager to install is '%s'. Do you want to install it ? (Y/n) : ") % "SDDM",
            default=True)

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % ("SDDM" if self.display_manager else _("none")))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        if self.display_manager:
            execute('arch-chroot /mnt bash -c "systemctl enable sddm"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")
