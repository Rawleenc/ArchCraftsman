"""
The sway bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.partitioninginfo import PartitioningInfo
from src.prelaunchinfo import PreLaunchInfo
from src.utils import print_sub_step, execute

_ = I18n().gettext


class Sway(Bundle):
    """
    Bundle class.
    """

    def packages(self, system_info) -> list[str]:
        packages = ["sway", "dmenu", "bemenu-wayland", "j4-dmenu-desktop", "foot", "grim", "mako", "slurp", "swayidle",
                    "swaylock", "swayimg", "waybar", "swaybg", "wf-recorder", "wl-clipboard", "xorg-xwayland",
                    "alsa-utils", "pulseaudio", "pulseaudio-alsa", "pavucontrol", "system-config-printer", "acpid",
                    "brightnessctl", "playerctl", "gammastep", "dex", "libindicator-gtk2", "libindicator-gtk3",
                    "gnome-keyring", "xdg-desktop-portal", "xdg-desktop-portal-wlr"]
        return packages

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % _("none"))

    def configure(self, system_info, pre_launch_info: PreLaunchInfo, partitioning_info: PartitioningInfo):
        execute('arch-chroot /mnt bash -c "systemctl enable acpid"')
        pre_launch_info.setup_chroot_keyboard()
        if "fr" in pre_launch_info.keymap:
            execute("echo 'XKB_DEFAULT_LAYOUT=fr' >> /mnt/etc/environment")
