"""
The enlightenment bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.localesetup import setup_chroot_keyboard
from src.utils import print_sub_step, execute

_ = I18n().gettext


class Enlightenment(Bundle):
    """
    Bundle class.
    """

    def packages(self, system_info) -> [str]:
        packages = ["enlightenment", "terminology", "xorg-server", "xorg-xinit", "alsa-utils", "pulseaudio",
                    "pulseaudio-alsa", "pavucontrol", "system-config-printer", "network-manager-applet", "acpid"]
        return packages

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % _("none"))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        execute('arch-chroot /mnt bash -c "systemctl enable acpid"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")
