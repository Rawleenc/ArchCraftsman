import os

from src.bundles.bundle import Bundle
from src.bundles.i18n import I18n
from src.setups import setup_chroot_keyboard
from src.utils import print_sub_step

_ = I18n().gettext

class I3(Bundle):
    """
    Bundle class.
    """

    def packages(self, system_info) -> [str]:
        packages = ["i3", "rofi", "dmenu", "perl", "alacritty", "xorg-server", "xorg-xinit", "alsa-utils", "pulseaudio",
                    "pulseaudio-alsa", "pavucontrol", "system-config-printer", "network-manager-applet", "acpid",
                    "gnome-keyring", "dex"]
        return packages

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % _("none"))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        os.system('arch-chroot /mnt bash -c "systemctl enable acpid"')
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")
