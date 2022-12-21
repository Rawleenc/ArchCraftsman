import os

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.localesetup import setup_chroot_keyboard
from src.utils import print_sub_step

_ = I18n().gettext


class Sway(Bundle):
    """
    Bundle class.
    """

    def packages(self, system_info) -> [str]:
        packages = ["sway", "dmenu", "bemenu-wayland", "j4-dmenu-desktop", "foot", "grim", "mako", "slurp", "swayidle",
                    "swaylock", "swayimg", "waybar", "swaybg", "wf-recorder", "wl-clipboard", "xorg-xwayland",
                    "alsa-utils", "pulseaudio", "pulseaudio-alsa", "pavucontrol", "system-config-printer",
                    "network-manager-applet", "acpid", "brightnessctl", "playerctl", "gammastep", "dex",
                    "libindicator-gtk2", "libindicator-gtk3", "gnome-keyring", "xdg-desktop-portal",
                    "xdg-desktop-portal-wlr"]
        return packages

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % _("none"))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        os.system('arch-chroot /mnt bash -c "systemctl enable acpid"')
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            os.system("echo 'XKB_DEFAULT_LAYOUT=fr' >> /mnt/etc/environment")
            setup_chroot_keyboard("fr")
