import os

from src.archcraftsman import _
from src.bundles.bundle import Bundle
from src.setups import setup_chroot_keyboard
from src.utils import print_sub_step, prompt_bool


class Cinnamon(Bundle):
    """
    Bundle class.
    """
    display_manager = True

    def packages(self, system_info) -> [str]:
        packages = ["cinnamon", "metacity", "gnome-shell", "gnome-terminal", "blueberry", "cinnamon-translations",
                    "gnome-panel", "system-config-printer", "wget", "xorg-server", "alsa-utils", "pulseaudio",
                    "pulseaudio-alsa", "pavucontrol"]
        if self.display_manager:
            packages.extend(["lightdm", "lightdm-gtk-greeter", "lightdm-gtk-greeter-settings"])
        return packages

    def prompt_extra(self):
        self.display_manager = prompt_bool(
            _("The display manager to install is '%s'. Do you want to install it ? (Y/n) : ") % "LightDM",
            default=True)

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % ("LightDM" if self.display_manager else _("none")))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        if self.display_manager:
            os.system('arch-chroot /mnt bash -c "systemctl enable lightdm"')
        os.system(
            'sed -i "s|#logind-check-graphical=false|logind-check-graphical=true|g" /mnt/etc/lightdm/lightdm.conf')
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")