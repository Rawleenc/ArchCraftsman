"""
The xfce bundle module
"""
import os

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.localesetup import setup_chroot_keyboard
from src.utils import print_sub_step, prompt_bool

_ = I18n().gettext


class Xfce(Bundle):
    """
    Bundle class.
    """
    display_manager = True
    minimal = False

    def packages(self, system_info) -> [str]:
        packages = ["xfce4", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa", "pavucontrol",
                    "network-manager-applet"]
        if self.display_manager:
            packages.extend(["lightdm", "lightdm-gtk-greeter", "lightdm-gtk-greeter-settings"])
        if self.minimal is not True:
            packages.append("xfce4-goodies")
        return packages

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % ("LightDM" if self.display_manager else _("none")))
        if self.minimal:
            print_sub_step(_("Install a minimal environment."))

    def prompt_extra(self):
        self.display_manager = prompt_bool(
            _("The display manager to install is '%s'. Do you want to install it ? (Y/n) : ") % "LightDM",
            default=True)
        self.minimal = prompt_bool(
            _("Install a minimal environment ? (y/N/?) : "),
            default=False,
            help_msg=_("If yes, the script will not install any extra packages, only base packages."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        if self.display_manager:
            os.system('arch-chroot /mnt bash -c "systemctl enable lightdm"')
        os.system(
            'sed -i "s|#logind-check-graphical=false|logind-check-graphical=true|g" /mnt/etc/lightdm/lightdm.conf')
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")
