"""
The gnome bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.localesetup import setup_chroot_keyboard
from src.utils import print_sub_step, prompt_bool, execute

_ = I18n().gettext


class Gnome(Bundle):
    """
    Bundle class.
    """
    minimal = False

    def packages(self, system_info) -> [str]:
        packages = ["gnome", "alsa-utils", "pulseaudio", "pulseaudio-alsa", "xdg-desktop-portal",
                    "xdg-desktop-portal-gnome", "qt5-wayland"]
        if self.minimal is not True:
            packages.append("gnome-extra")
        return packages

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % "GDM")

    def prompt_extra(self):
        self.minimal = prompt_bool(
            _("Install a minimal environment ? (y/N/?) : "),
            default=False,
            help_msg=_("If yes, the script will not install any extra packages, only base packages."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        execute('arch-chroot /mnt bash -c "systemctl enable gdm"')
        execute('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")
