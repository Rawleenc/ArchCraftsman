"""
The budgie bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.localesetup import setup_chroot_keyboard
from src.partitioninginfo import PartitioningInfo
from src.utils import print_sub_step, prompt_bool, execute

_ = I18n().gettext


class Budgie(Bundle):
    """
    Bundle class.
    """
    display_manager = True

    def packages(self, system_info) -> list[str]:
        packages = ["budgie-desktop", "budgie-desktop-view", "budgie-screensaver", "gnome-control-center",
                    "gnome-terminal", "nautilus", "xorg-server", "alsa-utils", "pulseaudio",
                    "pulseaudio-alsa", "pavucontrol", "arc-gtk-theme", "arc-icon-theme"]
        if self.display_manager:
            packages.extend(["lightdm", "lightdm-gtk-greeter", "lightdm-gtk-greeter-settings"])
        return packages

    def prompt_extra(self):
        self.display_manager = prompt_bool(
            _("The display manager to install is '%s'. Do you want to install it ?") % "LightDM",
            default=True)

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % ("LightDM" if self.display_manager else _("none")))

    def configure(self, system_info, pre_launch_info, partitioning_info: PartitioningInfo):
        if self.display_manager:
            execute('arch-chroot /mnt bash -c "systemctl enable lightdm"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")
