"""
LICENSE
ArchCraftsman, The careful yet very fast Arch Linux Craftsman.
Copyright (C) 2021  Rawleenc

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

DISCLAIMER
ArchCraftsman  Copyright (C) 2022  Rawleenc

This program comes with ABSOLUTELY NO WARRANTY; See the
GNU General Public License for more details.

This is free software, and you are welcome to redistribute it
under certain conditions; See the GNU General Public License for more details.
"""
import getpass
import gettext
import glob
import json
import os
import re
import readline
import subprocess
import urllib.request

RED = "\033[0;31m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
ORANGE = "\033[0;33m"
NOCOLOR = "\033[0m"


def complete(text, state):
    """
    A file path completer.
    :param text:
    :param state:
    :return:
    """
    return (glob.glob(text + '*') + [None])[state]


readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)


def is_bios() -> bool:
    """
    Check if live system run on a bios.
    :return:
    """
    return not os.path.exists("/sys/firmware/efi")


class Bundle:
    """
    A class to represent a bootloader.
    """
    name: str

    def __init__(self, name: str):
        self.name = name

    def packages(self, system_info: {}) -> [str]:  # pylint: disable=unused-argument
        """
        Bundle's packages retrieving method.
        """
        return []

    def prompt_extra(self):
        """
        Bundle's extra options prompting method.
        """

    def print_resume(self):
        """
        Bundle's print resume method.
        """

    def configure(self, system_info, pre_launch_info, partitioning_info):
        """
        Bundle configuration method.
        :param system_info:
        :param pre_launch_info:
        :param partitioning_info:
        """


def get_supported_kernels(get_default: bool = False) -> str or []:
    """
    The method to get all supported kernels.
    :return:
    """
    return "current" if get_default else ["current", "lts", "zen", "hardened"]


class LinuxCurrent(Bundle):
    """
    The Linux current kernel class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["linux", "linux-headers"]

    def print_resume(self):
        print_sub_step(_("Install Linux current kernel."))


class LinuxLts(Bundle):
    """
    The Linux LTS kernel class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["linux-lts", "linux-lts-headers"]

    def print_resume(self):
        print_sub_step(_("Install Linux LTS kernel."))


class LinuxZen(Bundle):
    """
    The Linux zen kernel class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["linux-zen", "linux-zen-headers"]

    def print_resume(self):
        print_sub_step(_("Install Linux zen kernel."))


class LinuxHardened(Bundle):
    """
    The Linux hardened kernel class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["linux-hardened", "linux-hardened-headers"]

    def print_resume(self):
        print_sub_step(_("Install Linux hardened kernel."))


class NvidiaDriver(Bundle):
    """
    The Nvidia driver class.
    """

    def packages(self, system_info: {}) -> [str]:
        if system_info["kernel"] and system_info["kernel"].name == "lts":
            return ["nvidia-lts"]
        return ["nvidia"]

    def print_resume(self):
        print_sub_step(_("Install proprietary Nvidia driver."))


class TerminusFont(Bundle):
    """
    The Terminus console font class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["terminus-font"]

    def print_resume(self):
        print_sub_step(_("Install terminus console font."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        os.system(f'echo "FONT={pre_launch_info["live_console_font"]}" >>/mnt/etc/vconsole.conf')


class Microcodes(Bundle):
    """
    The Microcodes class.
    """

    def __init__(self):
        super().__init__(re.sub('\\s+', '', os.popen('grep </proc/cpuinfo "vendor" | uniq').read()).split(":")[1])

    def packages(self, system_info: {}) -> [str]:
        if self.name == "GenuineIntel":
            return ["intel-ucode"]
        if self.name == "AuthenticAMD":
            return ["amd-ucode"]
        return []

    def microcode_img(self) -> str or None:
        """
        The microcode img file name retrieving method.
        """
        if self.name == "GenuineIntel":
            return "/intel-ucode.img"
        if self.name == "AuthenticAMD":
            return "/amd-ucode.img"
        return None

    def print_resume(self):
        if self.name in {"GenuineIntel", "AuthenticAMD"}:
            print_sub_step(_("Microcodes to install : %s") % self.name)


class Grub(Bundle):
    """
    The Grub Bootloader class.
    """

    def packages(self, system_info) -> [str]:
        return ["grub"]

    def configure(self, system_info: dict, pre_launch_info: dict, partitioning_info: dict):
        if is_bios():
            os.system(f'arch-chroot /mnt bash -c "grub-install --target=i386-pc {partitioning_info["main_disk"]}"')
        else:
            os.system(
                'arch-chroot /mnt bash -c "grub-install --target=x86_64-efi --efi-directory=/boot/efi '
                '--bootloader-id=\'Arch Linux\'"')
        os.system('sed -i "/^GRUB_CMDLINE_LINUX=.*/a GRUB_DISABLE_OS_PROBER=false" /mnt/etc/default/grub')
        if partitioning_info["part_format_type"][partitioning_info["root_partition"]] in {"ext4"}:
            os.system('sed -i "s|GRUB_DEFAULT=.*|GRUB_DEFAULT=saved|g" /mnt/etc/default/grub')
            os.system('sed -i "/^GRUB_DEFAULT=.*/a GRUB_SAVEDEFAULT=true" /mnt/etc/default/grub')
        os.system('arch-chroot /mnt bash -c "grub-mkconfig -o /boot/grub/grub.cfg"')


def get_supported_desktop_environments(get_default: bool = False) -> str or []:
    """
    The method to get all supported desktop environments.
    :return:
    """
    return _("none") if get_default else ["gnome", "plasma", "xfce", "budgie", "cinnamon", "cutefish", "deepin", "lxqt",
                                          "mate", "enlightenment",
                                          "i3", "sway", _("none")]


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
        os.system('arch-chroot /mnt bash -c "systemctl enable gdm"')
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")


class Plasma(Bundle):
    """
    Bundle class.
    """
    minimal = False
    plasma_wayland = False

    def packages(self, system_info) -> [str]:
        packages = ["plasma", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa",
                    "xdg-desktop-portal", "xdg-desktop-portal-kde"]
        if self.plasma_wayland:
            packages.extend(["plasma-wayland-session", "qt5-wayland"])
            if "nvidia" in [bundle.name for bundle in system_info["bundles"]]:
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
            _("Install a minimal environment ? (y/N/?) : "),
            default=False,
            help_msg=_("If yes, the script will not install any extra packages, only base packages."))
        self.plasma_wayland = prompt_bool(_("Install Wayland support for the plasma session ? (y/N) : "),
                                          default=False)

    def configure(self, system_info, pre_launch_info, partitioning_info):
        os.system('arch-chroot /mnt bash -c "systemctl enable sddm"')
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")


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


class Budgie(Bundle):
    """
    Bundle class.
    """
    display_manager = True

    def packages(self, system_info) -> [str]:
        packages = ["budgie-desktop", "budgie-desktop-view", "budgie-screensaver", "gnome-control-center",
                    "network-manager-applet", "gnome-terminal", "nautilus", "xorg-server", "alsa-utils", "pulseaudio",
                    "pulseaudio-alsa", "pavucontrol", "arc-gtk-theme", "arc-icon-theme"]
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
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")


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


class Cutefish(Bundle):
    """
    Bundle class.
    """
    display_manager = True

    def packages(self, system_info) -> [str]:
        packages = ["cutefish", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa", "pavucontrol"]
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
            os.system('arch-chroot /mnt bash -c "systemctl enable sddm"')
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")


class Deepin(Bundle):
    """
    Bundle class.
    """
    minimal = False

    def packages(self, system_info) -> [str]:
        packages = ["deepin", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa"]
        if self.minimal is not True:
            packages.append("deepin-extra")
        return packages

    def print_resume(self):
        print_sub_step(_("Desktop environment : %s") % self.name)
        print_sub_step(_("Display manager : %s") % "LightDM")
        if self.minimal:
            print_sub_step(_("Install a minimal environment."))

    def prompt_extra(self):
        self.minimal = prompt_bool(
            _("Install a minimal environment ? (y/N/?) : "),
            default=False,
            help_msg=_("If yes, the script will not install any extra packages, only base packages."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        os.system('arch-chroot /mnt bash -c "systemctl enable lightdm"')
        os.system(
            'sed -i "s|#logind-check-graphical=false|logind-check-graphical=true|g" /mnt/etc/lightdm/lightdm.conf')
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")


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
            os.system('arch-chroot /mnt bash -c "systemctl enable sddm"')
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")


class Mate(Bundle):
    """
    Bundle class.
    """
    display_manager = True
    minimal = False

    def packages(self, system_info) -> [str]:
        packages = ["mate", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa", "network-manager-applet"]
        if self.display_manager:
            packages.extend(["lightdm", "lightdm-gtk-greeter", "lightdm-gtk-greeter-settings"])
        if self.minimal is not True:
            packages.append("mate-extra")
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
        os.system('arch-chroot /mnt bash -c "systemctl enable acpid"')
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in pre_launch_info["keymap"]:
            setup_chroot_keyboard("fr")


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


class Cups(Bundle):
    """
    Cups class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["cups", "cups-pdf", "avahi", "samba", "foomatic-db-engine", "foomatic-db", "foomatic-db-ppds",
                "foomatic-db-nonfree-ppds", "foomatic-db-gutenprint-ppds", "gutenprint", "ghostscript"]

    def print_resume(self):
        print_sub_step(_("Install Cups."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        os.system('arch-chroot /mnt bash -c "systemctl enable avahi-daemon"')
        os.system('arch-chroot /mnt bash -c "systemctl enable cups"')
        os.system('arch-chroot /mnt bash -c "systemctl enable cups-browsed"')


class GrmlZsh(Bundle):
    """
    Grml ZSH config class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["zsh", "zsh-completions", "grml-zsh-config"]

    def print_resume(self):
        print_sub_step(_("Install ZSH with GRML configuration."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        os.system('arch-chroot /mnt bash -c "chsh --shell /bin/zsh"')
        os.system(f'arch-chroot /mnt bash -c "chsh --shell /bin/zsh {system_info["user_name"]}"')


def get_main_fonts() -> [str]:
    """
    The method to get the package list of the main fonts group.
    :return:
    """
    return ["gnu-free-fonts", "noto-fonts", "ttf-bitstream-vera", "ttf-dejavu", "ttf-hack", "ttf-droid",
            "ttf-fira-code", "ttf-fira-mono", "ttf-fira-sans", "ttf-font-awesome", "ttf-inconsolata",
            "ttf-input", "ttf-liberation", "ttf-nerd-fonts-symbols-2048-em", "ttf-opensans", "ttf-roboto",
            "ttf-roboto-mono", "ttf-ubuntu-font-family", "ttf-jetbrains-mono", "otf-font-awesome", "noto-fonts-emoji"]


class MainFonts(Bundle):
    """
    The main fonts class.
    """

    def packages(self, system_info: {}) -> [str]:
        return get_main_fonts()

    def print_resume(self):
        print_sub_step(_("Install a set of main fonts."))


def get_main_file_systems() -> [str]:
    """
    The method to get the package list of the main file systems group.
    :return:
    """
    return ["btrfs-progs", "dosfstools", "exfatprogs", "f2fs-tools", "e2fsprogs", "jfsutils", "nilfs-utils",
            "ntfs-3g", "reiserfsprogs", "udftools", "xfsprogs"]


class MainFileSystems(Bundle):
    """
    The main file systems class.
    """

    def packages(self, system_info: {}) -> [str]:
        return get_main_file_systems()

    def print_resume(self):
        print_sub_step(_("Install main file systems support."))


class Zram(Bundle):
    """
    The ZRAM class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["zram-generator"]

    def print_resume(self):
        print_sub_step(_("Install and enable ZRAM."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        content = [
            "[zram0]\n",
            "zram-size = ram / 2\n"
        ]
        with open("/mnt/etc/systemd/zram-generator.conf", "w", encoding="UTF-8") as zram_config_file:
            zram_config_file.writelines(content)


class PipeWire(Bundle):
    """
    The PipeWire class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["pipewire", "pipewire-alsa", "pipewire-audio", "pipewire-jack", "pipewire-media-session",
                "pipewire-pulse", "pipewire-v4l2", "pipewire-x11-bell", "pipewire-zeroconf"]

    def print_resume(self):
        print_sub_step(_("Install PipeWire."))


def process_bundle(name: str) -> Bundle or None:
    """
    Process a bundle name into a Bundle object.
    :param name:
    :return:
    """
    bundle = None
    match name:
        case "current":
            bundle = LinuxCurrent("current")
        case "lts":
            bundle = LinuxLts("lts")
        case "zen":
            bundle = LinuxZen("zen")
        case "hardened":
            bundle = LinuxHardened("hardened")
        case "grub":
            bundle = Grub("grub")
        case "gnome":
            bundle = Gnome("gnome")
        case "plasma":
            bundle = Plasma("plasma")
        case "xfce":
            bundle = Xfce("xfce")
        case "budgie":
            bundle = Budgie("budgie")
        case "cinnamon":
            bundle = Cinnamon("cinnamon")
        case "cutefish":
            bundle = Cutefish("cutefish")
        case "deepin":
            bundle = Deepin("deepin")
        case "lxqt":
            bundle = Lxqt("lxqt")
        case "mate":
            bundle = Mate("mate")
        case "enlightenment":
            bundle = Enlightenment("enlightenment")
        case "i3":
            bundle = I3("i3")
        case "sway":
            bundle = Sway("sway")
    return bundle


class Partition:
    """
    A class to represent a partition.
    """
    path: str
    size: int
    part_type: str
    fs_type: str

    def __init__(self, part_str: str = None):
        """
        Partition initialisation.
        """
        if part_str is None:
            self.path = ""
            self.size = 0
            self.part_type = ""
            self.fs_type = ""
        else:
            self.path = part_str.split(" ")[0]
            self.size = from_iec(re.sub('\\s', '', os.popen(f'lsblk -nl "{self.path}" -o SIZE').read()))
            self.part_type = str(
                re.sub('[^a-zA-Z\\d ]', '', os.popen(f'lsblk -nl "{self.path}" -o PARTTYPENAME').read()))
            self.fs_type = str(
                re.sub('[^a-zA-Z\\d ]', '', os.popen(f'lsblk -nl "{self.path}" -o FSTYPE').read()))

    def __str__(self) -> str:
        """
        Partition str formatting.
        """
        return f"'{self.path}' - '{self.size}' - '{self.part_type}' - '{self.fs_type}'"


class Disk:
    """
    A class to represent a disk.
    """
    path: str
    partitions: list
    total: int
    free_space: int

    def __init__(self, path: str):
        """
        Disk initialisation.
        """
        self.path = path
        detected_partitions = os.popen(f'lsblk -nl "{path}" -o PATH,TYPE | grep part').read()
        self.partitions = []
        for partition_info in detected_partitions.splitlines():
            self.partitions.append(Partition(partition_info))
        self.total = int(os.popen(f'lsblk -b --output SIZE -n -d "{self.path}"').read())
        if len(self.partitions) > 0:
            sector_size = int(
                re.sub('\\s', '',
                       os.popen(f'lsblk {path} -o PATH,TYPE,PHY-SEC | grep disk | awk \'{{print $3}}\'').read()))
            last_partition_path = [p.path for p in self.partitions][len(self.partitions) - 1]
            last_sector = int(
                re.sub('\\s', '', os.popen(f'fdisk -l | grep {last_partition_path} | awk \'{{print $3}}\'').read()))
            self.free_space = self.total - (last_sector * sector_size)
        else:
            self.free_space = self.total

    def get_efi_partition(self) -> Partition:
        """
        The Disk method to get the EFI partition if it exist. Else return an empty partition object.
        """
        try:
            return [p for p in self.partitions if "EFI" in p.part_type].pop()
        except IndexError:
            return Partition()

    def __str__(self) -> str:
        """
        Disk str formatting
        """
        return "\n".join([str(p) for p in self.partitions])


def print_error(message: str, do_pause: bool = True):
    """
    A method to print an error.
    :param message:
    :param do_pause:
    :return:
    """
    print(f'\n{RED}  /!\\ {message}{NOCOLOR}\n')
    if do_pause:
        pause(end_newline=True)


def print_step(message: str, clear: bool = True):
    """
    A method to print a step message.
    :param message:
    :param clear:
    """
    if clear:
        os.system('clear')
    print(f'\n{GREEN}{message}{NOCOLOR}')


def print_sub_step(message: str):
    """
    A method to print a sub step message.
    :param message:
    """
    print(f'{CYAN}  * {message}{NOCOLOR}')


def print_help(message: str, do_pause: bool = False):
    """
    A method to print an help message.
    :param message:
    :param do_pause:
    :return:
    """
    print_step(_("Help :"), clear=False)
    print_sub_step(message)
    if do_pause:
        pause(end_newline=True)


def prompt(message: str, default: str = None, help_msg: str = None) -> str:
    """
    A method to prompt for a user input.
    :param message:
    :param default:
    :param help_msg:
    :return:
    """
    user_input_ok = False
    user_input = None
    while not user_input_ok:
        user_input = input(f'{ORANGE}{message}{NOCOLOR}')
        if user_input == "?" and help_msg and help_msg != "":
            print_help(help_msg)
            continue
        if user_input == "" and default:
            user_input = default
        user_input_ok = True
    return user_input


def prompt_ln(message: str, default: str = None, help_msg: str = None) -> str:
    """
    A method to prompt for a user input with a new line for the user input.
    :param message:
    :param default:
    :param help_msg:
    :return:
    """
    return prompt(f'{message}\n', default=default, help_msg=help_msg)


def prompt_bool(message: str, default: bool = True, help_msg: str = None) -> bool:
    """
    A method to prompt for a boolean choice.
    :param message:
    :param default:
    :param help_msg:
    :return:
    """
    if not default:
        return prompt(f'{message}', help_msg=help_msg).upper() in {"Y", "O"}
    return prompt(f'{message}', help_msg=help_msg).upper() != "N"


def prompt_passwd(message: str):
    """
    A method to prompt for a password without displaying an echo.
    :param message:
    :return:
    """
    return getpass.getpass(prompt=f'{ORANGE}{message}{NOCOLOR}')


def prompt_bundle(supported_msg: str, message: str, error_msg: str, default_bundle: str,
                  supported_bundles: [str]) -> Bundle or None:
    """
    A method to prompt for a bundle.
    :param supported_msg:
    :param message:
    :param error_msg:
    :param default_bundle:
    :param supported_bundles:
    :return:
    """
    print_step(supported_msg, clear=False)
    print_sub_step(", ".join(supported_bundles))
    print('')
    bundle_ok = False
    bundle = None
    while not bundle_ok:
        bundle_name = prompt_ln(
            message % default_bundle,
            default=default_bundle).lower()
        if bundle_name in supported_bundles:
            bundle_ok = True
            bundle = process_bundle(bundle_name)
        else:
            print_error(error_msg % bundle_name, do_pause=False)
            continue
    if bundle:
        bundle.prompt_extra()
    return bundle


def pause(start_newline: bool = False, end_newline: bool = False):
    """
    A method to insert a one key press pause.
    :param start_newline:
    :param end_newline:
    """
    message = _("Press any key to continue...")
    if start_newline:
        print("")
    print(f'{ORANGE}{message}{NOCOLOR}')
    os.system('read -n 1 -sr')
    if end_newline:
        print("")


def locale_setup(keymap: str = "de-latin1", global_language: str = "EN") -> str:
    """
    The method to setup environment locale.
    :param keymap:
    :param global_language:
    :return: The configured live system console font (terminus 16 or 32)
    """
    print_step(_("Configuring live environment..."), clear=False)
    os.system(f'loadkeys "{keymap}"')
    font = 'ter-v16b'
    os.system('setfont ter-v16b')
    dimensions = os.popen('stty size').read().split(" ")
    if dimensions and len(dimensions) > 0 and int(dimensions[0]) >= 80:
        font = 'ter-v32b'
        os.system('setfont ter-v32b')
    if global_language == "FR":
        os.system('sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /etc/locale.gen')
        os.system('locale-gen')
        os.putenv('LANG', 'fr_FR.UTF-8')
        os.putenv('LANGUAGE', 'fr_FR.UTF-8')
    else:
        os.putenv('LANG', 'en_US.UTF-8')
        os.putenv('LANGUAGE', 'en_US.UTF-8')
    return font


def setup_chroot_keyboard(layout: str):
    """
    The method to set the X keyboard of the chrooted system.
    :param layout:
    """
    content = [
        "Section \"InputClass\"\n",
        "    Identifier \"system-keyboard\"\n",
        "    MatchIsKeyboard \"on\"\n",
        f"    Option \"XkbLayout\" \"{layout}\"\n",
        "EndSection\n"
    ]
    os.system("mkdir --parents /mnt/etc/X11/xorg.conf.d/")
    with open("/mnt/etc/X11/xorg.conf.d/00-keyboard.conf", "w", encoding="UTF-8") as keyboard_config_file:
        keyboard_config_file.writelines(content)


def ask_swapfile_size(disk: Disk) -> str:
    """
    The method to ask the user for the swapfile size.
    :return:
    """
    swapfile_ok = False
    swapfile_size = ""
    swapfile_size_pattern = re.compile("^(\\d*[.,]\\d+|\\d+)([GMk])$")
    default_swapfile_size = to_iec(int(disk.total / 32))
    while not swapfile_ok:
        swapfile_size = prompt(_("Swapfile size ? (%s, type '0' for none) : ") % default_swapfile_size,
                               default=default_swapfile_size)
        if swapfile_size == "0":
            swapfile_size = None
            swapfile_ok = True
        elif swapfile_size_pattern.match(swapfile_size):
            swapfile_ok = True
        else:
            print_error("Invalid swapfile size.")
    return swapfile_size


def get_supported_format_types(get_default: bool = False) -> str or []:
    """
    The method to get all supported format types.
    :return:
    """
    return "ext4" if get_default else ["ext4", "btrfs"]


def ask_format_type() -> str:
    """
    The method to ask the user for the format type.
    :return:
    """
    default_format_type = get_supported_format_types(get_default=True)
    format_type_ok = False
    format_type = None
    print_step(_("Supported format types : "), clear=False)
    print_sub_step(", ".join(get_supported_format_types()))
    while not format_type_ok:
        format_type = prompt_ln(
            _("Which format type do you want ? (%s) : ") % default_format_type, default=default_format_type).lower()
        if format_type in get_supported_format_types():
            format_type_ok = True
        else:
            print_error(_("Format type '%s' is not supported.") % format_type, do_pause=False)
            continue
    return format_type


def manual_partitioning() -> {}:
    """
    The method to proceed to the manual partitioning.=
    :return:
    """
    partitioning_info = {"partitions": [], "part_type": {}, "part_mount_point": {}, "part_format": {},
                         "part_format_type": {}, "root_partition": None, "swapfile_size": None, "main_disk": None}
    user_answer = False
    partitioned_disks = set()
    while not user_answer:
        print_step(_("Manual partitioning :"))
        print_sub_step(_("Partitioned drives so far : %s") % " ".join(partitioned_disks))
        os.system('fdisk -l')
        target_disk = prompt(
            _("Which drive do you want to partition ? (type the entire name, for example '/dev/sda') : "))
        if not os.path.exists(target_disk):
            print_error(_("The chosen target drive doesn't exist."))
            continue
        partitioned_disks.add(target_disk)
        os.system(f'cfdisk "{target_disk}"')
        print_step(_("Manual partitioning :"))
        print_sub_step(_("Partitioned drives so far : %s") % " ".join(partitioned_disks))
        os.system('fdisk -l')
        other_drive = prompt_bool(_("Do you want to partition an other drive ? (y/N) : "), default=False)
        if other_drive:
            continue
        for disk in partitioned_disks:
            detected_partitions = os.popen(
                f'lsblk -nl "{disk}" -o PATH,PARTTYPENAME | grep -iE "linux|efi|swap" | awk \'{{print $1}}\'').read()
            for partition in detected_partitions.splitlines():
                partitioning_info["partitions"].append(partition)
        print_step(_("Detected target drive partitions : %s") % " ".join(partitioning_info["partitions"]))
        for partition in partitioning_info["partitions"]:
            print_sub_step(_("Partition : %s") % re.sub('\n', '', os.popen(
                f'lsblk -nl "{partition}" -o PATH,SIZE,PARTTYPENAME').read()))
            if is_bios():
                partition_type = prompt(
                    _("What is the role of this partition ? (1: Root, 2: Home, 3: Swap, 4: Not used, other: Other) : "))
            else:
                partition_type = prompt(
                    _("What is the role of this partition ? (0: EFI, 1: Root, 2: Home, 3: Swap, 4: Not used, "
                      "other: Other) : "))
            if not is_bios() and partition_type == "0":
                partitioning_info["part_type"][partition] = "EFI"
                partitioning_info["part_mount_point"][partition] = "/boot/efi"
                partitioning_info["part_format"][partition] = prompt_bool(_("Format the EFI partition ? (Y/n) : "))
                if partitioning_info["part_format"].get(partition):
                    partitioning_info["part_format_type"][partition] = "vfat"
            elif partition_type == "1":
                partitioning_info["part_type"][partition] = "ROOT"
                partitioning_info["part_mount_point"][partition] = "/"
                partitioning_info["part_format_type"][partition] = ask_format_type()
                partitioning_info["root_partition"] = partition
                main_disk_label = re.sub('\\s+', '', os.popen(f'lsblk -ndo PKNAME {partition}').read())
                partitioning_info["main_disk"] = f'/dev/{main_disk_label}'
            elif partition_type == "2":
                partitioning_info["part_type"][partition] = "HOME"
                partitioning_info["part_mount_point"][partition] = "/home"
                partitioning_info["part_format"][partition] = prompt_bool(_("Format the Home partition ? (Y/n) : "))
                if partitioning_info["part_format"].get(partition):
                    partitioning_info["part_format_type"][partition] = ask_format_type()
            elif partition_type == "3":
                partitioning_info["part_type"][partition] = "SWAP"
            elif partition_type == "4":
                continue
            else:
                partitioning_info["part_type"][partition] = "OTHER"
                partitioning_info["part_mount_point"][partition] = prompt(
                    _("What is the mounting point of this partition ? : "))
                partitioning_info["part_format"][partition] = prompt_bool(
                    _("Format the %s partition ? (Y/n) : ") % partition)
                if partitioning_info["part_format"].get(partition):
                    partitioning_info["part_format_type"][partition] = ask_format_type()
        if not is_bios() and "EFI" not in partitioning_info["part_type"].values():
            print_error(_("The EFI partition is required for system installation."))
            partitioning_info["partitions"].clear()
            partitioned_disks.clear()
            continue
        if "ROOT" not in partitioning_info["part_type"].values():
            print_error(_("The Root partition is required for system installation."))
            partitioning_info["partitions"].clear()
            partitioned_disks.clear()
            continue
        if "SWAP" not in partitioning_info["part_type"].values():
            partitioning_info["swapfile_size"] = ask_swapfile_size(Disk(partitioning_info["main_disk"]))
        print_step(_("Summary of choices :"))
        for partition in partitioning_info["partitions"]:
            if partitioning_info["part_format"].get(partition):
                formatting = _("yes")
            else:
                formatting = _("no")
            if partitioning_info["part_type"].get(partition) == "EFI":
                print_sub_step(_("EFI partition : %s (mounting point : %s, format %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition), formatting,
                                  partitioning_info["part_format_type"].get(partition)))
            if partitioning_info["part_type"].get(partition) == "ROOT":
                print_sub_step(_("ROOT partition : %s (mounting point : %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition),
                                  partitioning_info["part_format_type"].get(partition)))
            if partitioning_info["part_type"].get(partition) == "HOME":
                print_sub_step(_("Home partition : %s (mounting point : %s, format %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition), formatting,
                                  partitioning_info["part_format_type"].get(partition)))
            if partitioning_info["part_type"].get(partition) == "SWAP":
                print_sub_step(_("Swap partition : %s") % partition)
            if partitioning_info["part_type"].get(partition) == "OTHER":
                print_sub_step(_("Other partition : %s (mounting point : %s, format %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition), formatting,
                                  partitioning_info["part_format_type"].get(partition)))
        if "SWAP" not in partitioning_info["part_type"].values() and partitioning_info["swapfile_size"]:
            print_sub_step(_("Swapfile size : %s") % partitioning_info["swapfile_size"])
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
        if not user_answer:
            partitioning_info["partitions"].clear()
            partitioned_disks.clear()
    return partitioning_info


def build_partition_name(disk_name: str, index: int) -> str or None:
    """
    A method to build a partition name with a disk and an index.
    :param disk_name:
    :param index:
    :return:
    """
    block_devices_str = os.popen('lsblk -J').read()
    block_devices_json = json.loads(block_devices_str)
    if block_devices_json is None or not isinstance(block_devices_json, dict) or "blockdevices" not in dict(
            block_devices_json):
        return None
    block_devices = dict(block_devices_json).get("blockdevices")
    if block_devices is None or not isinstance(block_devices, list):
        return None
    disk = next((d for d in block_devices if
                 d is not None and isinstance(d, dict) and "name" in d and dict(d).get("name") == os.path.basename(
                     disk_name)), None)
    if disk is None or not isinstance(disk, dict) or "children" not in dict(disk):
        return None
    partitions = dict(disk).get("children")
    if partitions is None or not isinstance(partitions, list) or len(list(partitions)) <= index:
        return None
    partition = list(partitions)[index]
    if partition is None or not isinstance(partition, dict) or "name" not in dict(partition):
        return None
    return f'/dev/{dict(partition).get("name")}'


def to_iec(size: int) -> str:
    """
    The method to convert a size in iec format.
    """
    return re.sub('\\s', '', os.popen(f'printf "{size}" | numfmt --to=iec').read())


def from_iec(size: str) -> int:
    """
    The method to convert an iec formatted size in bytes.
    """
    return int(re.sub('\\s', '', os.popen(f'printf "{size}" | numfmt --from=iec').read()))


def auto_partitioning() -> {}:
    """
    The method to proceed to the automatic partitioning.
    :return:
    """
    partitioning_info = {"partitions": [], "part_type": {}, "part_mount_point": {}, "part_format": {},
                         "part_format_type": {}, "root_partition": None, "swapfile_size": None, "main_disk": None}
    user_answer = False
    while not user_answer:
        print_step(_("Automatic partitioning :"))
        os.system("fdisk -l")
        target_disk = prompt(
            _("On which drive should Archlinux be installed ? (type the entire name, for example '/dev/sda') : "))
        if target_disk == "":
            print_error(_("You need to choose a target drive."))
            continue
        if not os.path.exists(target_disk):
            print_error(_("You need to choose a target drive."))
            continue
        partitioning_info["main_disk"] = target_disk
        disk = Disk(target_disk)
        swap_type = prompt(_("What type of Swap do you want ? (1: Partition, 2: None, other: File) : "))
        want_home = prompt_bool(_("Do you want a separated Home ? (Y/n) : "))
        part_format_type = ask_format_type()
        efi_partition = disk.get_efi_partition()
        if not is_bios() \
                and len(disk.partitions) > 0 \
                and efi_partition.path != "" \
                and efi_partition.fs_type == "vfat" \
                and disk.free_space > from_iec("32G"):
            want_dual_boot = prompt_bool(_("Do you want to install Arch Linux next to other systems ? (Y/n) : "))
        else:
            want_dual_boot = False
        if want_dual_boot:
            root_size = to_iec(int(disk.free_space / 4))
            swap_size = to_iec(int(disk.free_space / 32))
        else:
            root_size = to_iec(int(disk.total / 4))
            swap_size = to_iec(int(disk.total / 32))
        if swap_type != "1":
            if swap_type == "2":
                swap_size = None
            partitioning_info["swapfile_size"] = swap_size
        auto_part_str = ""
        index = 0
        if is_bios():
            # DOS LABEL
            auto_part_str += "o\n"  # Create a new empty DOS partition table
            # BOOT
            auto_part_str += "n\n"  # Add a new partition
            auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += "+1G\n"  # Last sector (Accept default: varies)
            auto_part_str += "a\n"  # Toggle bootable flag
            partition = build_partition_name(target_disk, index)
            partitioning_info["part_type"][partition] = "OTHER"
            partitioning_info["part_mount_point"][partition] = "/boot"
            partitioning_info["part_format"][partition] = True
            partitioning_info["part_format_type"][partition] = part_format_type
            partitioning_info["partitions"].append(partition)
            index += 1
        else:
            if not want_dual_boot:
                # GPT LABEL
                auto_part_str += "g\n"  # Create a new empty GPT partition table
                # EFI
                auto_part_str += "n\n"  # Add a new partition
                auto_part_str += " \n"  # Partition number (Accept default: auto)
                auto_part_str += " \n"  # First sector (Accept default: 1)
                auto_part_str += "+512M\n"  # Last sector (Accept default: varies)
                auto_part_str += "t\n"  # Change partition type
                auto_part_str += " \n"  # Partition number (Accept default: auto)
                auto_part_str += "1\n"  # Type EFI System
                partition = build_partition_name(target_disk, index)
                partitioning_info["part_format"][partition] = True
                partitioning_info["part_format_type"][partition] = "vfat"
                index += 1
            else:
                index += len(disk.partitions)
                partition = efi_partition.path
                partitioning_info["part_format"][partition] = False
            partitioning_info["part_type"][partition] = "EFI"
            partitioning_info["part_mount_point"][partition] = "/boot/efi"
            partitioning_info["partitions"].append(partition)
        if swap_type == "1":
            # SWAP
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += f'+{swap_size}\n'  # Last sector (Accept default: varies)
            auto_part_str += "t\n"  # Change partition type
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            if is_bios():
                auto_part_str += "82\n"  # Type Linux Swap
            else:
                auto_part_str += "19\n"  # Type Linux Swap
            partition = build_partition_name(target_disk, index)
            partitioning_info["part_type"][partition] = "SWAP"
            partitioning_info["partitions"].append(partition)
            index += 1
        if want_home:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += f'+{root_size}\n'  # Last sector (Accept default: varies)
            partition = build_partition_name(target_disk, index)
            partitioning_info["part_type"][partition] = "ROOT"
            partitioning_info["part_mount_point"][partition] = "/"
            partitioning_info["part_format_type"][partition] = part_format_type
            partitioning_info["root_partition"] = partition
            partitioning_info["partitions"].append(partition)
            index += 1
            # HOME
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            partition = build_partition_name(target_disk, index)
            partitioning_info["part_type"][partition] = "HOME"
            partitioning_info["part_mount_point"][partition] = "/home"
            partitioning_info["part_format"][partition] = True
            partitioning_info["part_format_type"][partition] = part_format_type
            partitioning_info["partitions"].append(partition)
            index += 1
        else:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            partition = build_partition_name(target_disk, index)
            partitioning_info["part_type"][partition] = "ROOT"
            partitioning_info["part_mount_point"][partition] = "/"
            partitioning_info["part_format_type"][partition] = part_format_type
            partitioning_info["root_partition"] = partition
            partitioning_info["partitions"].append(partition)
            index += 1
        # WRITE
        auto_part_str += "w\n"

        print_step(_("Summary of choices :"), clear=False)
        for partition in partitioning_info["partitions"]:
            if partitioning_info["part_format"].get(partition):
                formatting = _("yes")
            else:
                formatting = _("no")
            if partitioning_info["part_type"].get(partition) == "EFI":
                print_sub_step(_("EFI partition : %s (mounting point : %s, format %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition), formatting,
                                  partitioning_info["part_format_type"].get(partition)))
            if partitioning_info["part_type"].get(partition) == "ROOT":
                print_sub_step(_("ROOT partition : %s (mounting point : %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition),
                                  partitioning_info["part_format_type"].get(partition)))
            if partitioning_info["part_type"].get(partition) == "HOME":
                print_sub_step(_("Home partition : %s (mounting point : %s, format %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition), formatting,
                                  partitioning_info["part_format_type"].get(partition)))
            if partitioning_info["part_type"].get(partition) == "SWAP":
                print_sub_step(_("Swap partition : %s") % partition)
            if partitioning_info["part_type"].get(partition) == "OTHER":
                print_sub_step(_("Other partition : %s (mounting point : %s, format %s, format type %s)")
                               % (partition, partitioning_info["part_mount_point"].get(partition), formatting,
                                  partitioning_info["part_format_type"].get(partition)))
        if "SWAP" not in partitioning_info["part_type"].values() and swap_size:
            print_sub_step(_("Swapfile size : %s") % swap_size)
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
        if not user_answer:
            partitioning_info["partitions"].clear()
        else:
            os.system(f'echo -e "{auto_part_str}" | fdisk "{target_disk}" &>/dev/null')
    return partitioning_info


def environment_config(detected_language: str) -> {}:
    """
    The method to get environment configurations from the user.
    :param detected_language:
    :return:
    """
    pre_launch_info = {"global_language": None, "keymap": None}
    user_answer = False
    while not user_answer:
        print_step(_("Welcome to ArchCraftsman !"))
        if is_bios():
            print_error(
                _("BIOS detected ! The script will act accordingly. Don't forget to select a DOS label type before "
                  "partitioning."))

        print_step(_("Environment configuration : "), clear=False)

        supported_global_languages = ["FR", "EN"]
        if detected_language == "fr-FR":
            default_language = "FR"
        else:
            default_language = "EN"

        print_step(_("Supported languages : "), clear=False)
        print_sub_step(", ".join(supported_global_languages))
        print('')
        global_language_ok = False
        pre_launch_info["global_language"] = None
        pre_launch_info["keymap"] = None
        while not global_language_ok:
            pre_launch_info["global_language"] = prompt_ln(
                _("Choose your installation's language (%s) : ") % default_language,
                default=default_language).upper()
            if pre_launch_info["global_language"] in supported_global_languages:
                global_language_ok = True
            else:
                print_error(_("Global language '%s' is not supported.") % pre_launch_info["global_language"],
                            do_pause=False)
                continue

        if detected_language == "fr-FR":
            default_keymap = "fr-latin9"
        else:
            default_keymap = "de-latin1"

        keymap_ok = False
        while not keymap_ok:
            pre_launch_info["keymap"] = prompt_ln(_("Type your installation's keymap (%s) : ") % default_keymap,
                                                  default=default_keymap)
            if os.system(f'localectl list-keymaps | grep "^{pre_launch_info["keymap"]}$" &>/dev/null') == 0:
                keymap_ok = True
            else:
                print_error(_("Keymap %s doesn't exist.") % pre_launch_info["keymap"])
                continue

        print_step(_("Summary of choices :"), clear=False)
        print_sub_step(_("Your installation's language : %s") % pre_launch_info["global_language"])
        print_sub_step(_("Your installation's keymap : %s") % pre_launch_info["keymap"])
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
    return pre_launch_info


def ask_password(username: str = "root") -> str:
    """
    A method to ask a password to the user.
    :param username:
    :return:
    """
    password_confirm = None
    password = ""
    while password != password_confirm:
        print_sub_step(_("%s password configuration : ") % username)
        password = prompt_passwd(_("Enter the %s password : ") % username)
        password_confirm = prompt_passwd(_("Re-enter the %s password to confirm : ") % username)
        if password != password_confirm:
            print_error(_("Passwords entered don't match."))
    return password


def system_config(detected_timezone) -> {}:
    """
    The method to get system configurations from the user.
    :param detected_timezone:
    :return:
    """
    system_info = {}
    user_answer = False
    while not user_answer:
        print_step(_("System configuration : "))
        system_info["hostname"] = prompt_ln(_("What will be your hostname (archlinux) : "), default="archlinux")
        system_info["bundles"] = []

        system_info["kernel"] = prompt_bundle(_("Supported kernels : "),
                                              _("Choose your kernel (%s) : "),
                                              _("Kernel '%s' is not supported."),
                                              get_supported_kernels(get_default=True),
                                              get_supported_kernels())

        if prompt_bool(_("Install proprietary Nvidia driver ? (y/N) : "), default=False):
            system_info["bundles"].append(NvidiaDriver("nvidia"))

        if prompt_bool(_("Install terminus console font ? (y/N) : "), default=False):
            system_info["bundles"].append(TerminusFont("terminus"))

        system_info["bundles"].append(prompt_bundle(_("Supported desktop environments : "),
                                                    _("Install a desktop environment ? (%s) : "),
                                                    _("Desktop environment '%s' is not supported."),
                                                    get_supported_desktop_environments(get_default=True),
                                                    get_supported_desktop_environments()))

        if prompt_bool(_("Install Cups ? (y/N) : "), default=False):
            system_info["bundles"].append(Cups("cups"))

        if prompt_bool(_("Install ZSH with GRML configuration ? (y/N/?) : "), default=False,
                       help_msg=_(
                           "If yes, the script will install the ZSH shell with GRML "
                           "configuration. GRML is a ZSH pre-configuration used by Archlinux's "
                           "live environment.")):
            system_info["bundles"].append(GrmlZsh("grml"))

        if prompt_bool(_("Install a set of main fonts ? (y/N/?) : "), default=False,
                       help_msg=_("If yes, the following packages will be installed :\n%s") % " ".join(
                           get_main_fonts())):
            system_info["bundles"].append(MainFonts("mainfonts"))

        if prompt_bool(_("Install main file systems support ? (y/N/?) : "),
                       default=False, help_msg=_(
                    "If yes, the following packages will be installed :\n%s") % " ".join(get_main_file_systems())):
            system_info["bundles"].append(MainFileSystems("mainfilesystems"))

        if prompt_bool(_("Install and enable ZRAM ? (y/N/?) : "), default=False, help_msg=_(
                "ZRAM is a process to compress datas directly in the RAM instead of moving them in a swap. "
                "Enabled ZRAM will allow you to compress up to half of your RAM before having to swap. "
                "This method is more efficient than the swap and do not use your disk but is more CPU demanding. "
                "ZRAM is fully compatible with a swap, it just has a higher priority.")):
            system_info["bundles"].append(Zram("zram"))

        if prompt_bool(_("Install PipeWire ? (y/N/?) : "),
                       default=False, help_msg=_(
                    "If yes, the PipeWire multimedia framework will be installed to manage audio and video capture.")):
            system_info["bundles"].append(PipeWire("pipewire"))

        default_timezone_file = f'/usr/share/zoneinfo/{detected_timezone}'
        system_info["timezone"] = prompt_ln(_("Your timezone (%s) : ") % default_timezone_file,
                                            default=default_timezone_file)
        user_name_pattern = re.compile("^[a-z][-a-z\\d_]*$")
        user_name_ok = False
        while not user_name_ok:
            system_info["user_name"] = prompt_ln(_("Would you like to add a user? (type username, leave blank if "
                                                   "none) : "))
            if system_info["user_name"] and system_info["user_name"] != "" and not user_name_pattern.match(
                    system_info["user_name"]):
                print_error(_("Invalid user name."))
                continue
            user_name_ok = True
        system_info["user_full_name"] = ""
        if system_info["user_name"] != "":
            system_info["user_full_name"] = prompt_ln(
                _("What is the %s's full name (type the entire full name, leave blank if none) : ") % system_info[
                    "user_name"])

        pkgs_select_ok = False
        while not pkgs_select_ok:
            system_info["more_pkgs"] = set()
            more_pkgs_str = prompt_ln(
                _("Install more packages ? (type extra packages full names, example : 'htop neofetch', leave blank if "
                  "none) : "))
            pkgs_select_ok = True
            if more_pkgs_str != "":
                for pkg in more_pkgs_str.split():
                    if os.system(f'pacman -Si {pkg} &>/dev/null') != 0:
                        pkgs_select_ok = False
                        print_error(_("Package %s doesn't exist.") % pkg)
                        break
                    system_info["more_pkgs"].add(pkg)

        system_info["root_password"] = ask_password()
        if system_info["user_name"] != "":
            system_info["user_password"] = ask_password(system_info["user_name"])

        system_info["bootloader"] = Grub("grub")
        system_info["microcodes"] = Microcodes()

        print_step(_("Summary of choices :"))
        print_sub_step(_("Your hostname : %s") % system_info["hostname"])
        system_info["microcodes"].print_resume()
        if system_info["kernel"]:
            system_info["kernel"].print_resume()
        for bundle in system_info["bundles"]:
            if bundle is not None and isinstance(bundle, Bundle):
                bundle.print_resume()
        print_sub_step(_("Your timezone : %s") % system_info["timezone"])
        if system_info["user_name"] != "":
            print_sub_step(_("Additional user name : %s") % system_info["user_name"])
            if system_info["user_full_name"] != "":
                print_sub_step(_("User's full name : %s") % system_info["user_full_name"])
        if system_info["more_pkgs"]:
            print_sub_step(_("More packages to install : %s") % " ".join(system_info["more_pkgs"]))
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
    return system_info


def umount_partitions():
    """
    A method to unmount all mounted partitions.
    """
    print_step(_("Unmounting partitions..."), clear=False)
    swap = re.sub('\\s', '', os.popen('swapon --noheadings | awk \'{print $1}\'').read())
    if swap != "":
        os.system(f'swapoff {swap} &>/dev/null')

    os.system('umount -R /mnt &>/dev/null')


def format_partition(partition: str, format_type: str, mount_point: str, formatting: bool):
    """
    A method to compute and return an mkfs command.
    """
    match format_type:
        case "vfat":
            if formatting:
                os.system(f'mkfs.vfat "{partition}"')
            os.system(f'mkdir -p "/mnt{mount_point}"')
            os.system(f'mount "{partition}" "/mnt{mount_point}"')
        case "btrfs":
            if formatting:
                os.system(f'mkfs.btrfs -f "{partition}"')
            os.system(f'mkdir -p "/mnt{mount_point}"')
            os.system(f'mount -o compress=zstd "{partition}" "/mnt{mount_point}"')
        case _:
            if formatting:
                os.system(f'mkfs.ext4 "{partition}"')
            os.system(f'mkdir -p "/mnt{mount_point}"')
            os.system(f'mount "{partition}" "/mnt{mount_point}"')


def main(pre_launch_info):
    """ The main method. """
    system_info = system_config(pre_launch_info["detected_timezone"])
    btrfs_in_use = False

    print_step(_("Partitioning :"))
    want_auto_part = prompt_bool(_("Do you want an automatic partitioning ? (y/N) : "), default=False)
    if want_auto_part:
        partitioning_info = auto_partitioning()
    else:
        partitioning_info = manual_partitioning()

    print_step(_("Formatting and mounting partitions..."), clear=False)

    format_partition(partitioning_info["root_partition"],
                     partitioning_info["part_format_type"][partitioning_info["root_partition"]],
                     partitioning_info["part_mount_point"][partitioning_info["root_partition"]], True)
    if partitioning_info["part_format_type"][partitioning_info["root_partition"]] == "btrfs":
        btrfs_in_use = True

    for partition in partitioning_info["partitions"]:
        if partitioning_info["part_format_type"].get(partition) == "btrfs":
            btrfs_in_use = True
        if not is_bios() and partitioning_info["part_type"].get(partition) == "EFI":
            format_partition(partition, partitioning_info["part_format_type"].get(partition),
                             partitioning_info["part_mount_point"].get(partition),
                             partitioning_info["part_format"].get(partition))
        elif partitioning_info["part_type"].get(partition) == "HOME":
            format_partition(partition, partitioning_info["part_format_type"].get(partition),
                             partitioning_info["part_mount_point"].get(partition),
                             partitioning_info["part_format"].get(partition))
        elif partitioning_info["part_type"].get(partition) == "SWAP":
            os.system(f'mkswap "{partition}"')
            os.system(f'swapon "{partition}"')
        elif partitioning_info["part_type"].get(partition) == "OTHER":
            format_partition(partition, partitioning_info["part_format_type"].get(partition),
                             partitioning_info["part_mount_point"].get(partition),
                             partitioning_info["part_format"].get(partition))

    print_step(_("Updating mirrors..."), clear=False)
    os.system('reflector --verbose -phttps -f10 -l10 --sort rate -a2 --save /etc/pacman.d/mirrorlist')

    base_pkgs = set()
    base_pkgs.update(["base", "base-devel", "linux-firmware"])

    if system_info["kernel"]:
        base_pkgs.update(system_info["kernel"].packages(system_info))

    pkgs = set()
    pkgs.update(["man-db", "man-pages", "texinfo", "nano", "vim", "git", "curl", "os-prober", "efibootmgr",
                 "networkmanager", "xdg-user-dirs", "reflector", "numlockx", "net-tools", "polkit", "pacman-contrib"])

    if pre_launch_info["global_language"].lower() != "en" and os.system(
            f"pacman -Si man-pages-{pre_launch_info['global_language'].lower()} &>/dev/null") == 0:
        pkgs.add(f"man-pages-{pre_launch_info['global_language'].lower()}")

    if btrfs_in_use:
        pkgs.add("btrfs-progs")

    pkgs.update(system_info["microcodes"].packages(system_info))

    if system_info["bootloader"]:
        pkgs.update(system_info["bootloader"].packages(system_info))

    for bundle in system_info["bundles"]:
        pkgs.update(bundle.packages(system_info))

    if len(system_info["more_pkgs"]) > 0:
        pkgs.update(system_info["more_pkgs"])

    print_step(_("Installation of the base..."), clear=False)
    subprocess.run(f'pacstrap -K /mnt {" ".join(base_pkgs)}', shell=True, check=True)

    print_step(_("System configuration..."), clear=False)
    os.system('sed -i "s|#en_US.UTF-8 UTF-8|en_US.UTF-8 UTF-8|g" /mnt/etc/locale.gen')
    os.system('sed -i "s|#en_US ISO-8859-1|en_US ISO-8859-1|g" /mnt/etc/locale.gen')
    if pre_launch_info["global_language"] == "FR":
        os.system('sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /mnt/etc/locale.gen')
        os.system('sed -i "s|#fr_FR ISO-8859-1|fr_FR ISO-8859-1|g" /mnt/etc/locale.gen')
        os.system('echo "LANG=fr_FR.UTF-8" >/mnt/etc/locale.conf')
    else:
        os.system('echo "LANG=en_US.UTF-8" >/mnt/etc/locale.conf')
    os.system(f'echo "KEYMAP={pre_launch_info["keymap"]}" >/mnt/etc/vconsole.conf')
    os.system(f'echo "{system_info["hostname"]}" >/mnt/etc/hostname')
    os.system(f'''
        {{
            echo "127.0.0.1 localhost"
            echo "::1 localhost"
            echo "127.0.1.1 {system_info["hostname"]}.localdomain {system_info["hostname"]}"
        }} >>/mnt/etc/hosts
    ''')
    os.system('cp /etc/pacman.d/mirrorlist /mnt/etc/pacman.d/mirrorlist')

    print_step(_("Locales configuration..."), clear=False)
    os.system(f'arch-chroot /mnt bash -c "ln -sf {system_info["timezone"]} /etc/localtime"')
    os.system('arch-chroot /mnt bash -c "locale-gen"')

    print_step(_("Installation of the remaining packages..."), clear=False)
    os.system('sed -i "s|#Color|Color|g" /mnt/etc/pacman.conf')
    os.system('sed -i "s|#ParallelDownloads = 5|ParallelDownloads = 5\\nDisableDownloadTimeout|g" /mnt/etc/pacman.conf')
    subprocess.run(f'arch-chroot /mnt bash -c "pacman --noconfirm -Sy archlinux-keyring"', shell=True, check=True)
    subprocess.run(f'arch-chroot /mnt bash -c "pacman --noconfirm -Su"', shell=True, check=True)
    subprocess.run(f'arch-chroot /mnt bash -c "pacman --noconfirm -S {" ".join(pkgs)}"', shell=True, check=True)

    if "SWAP" not in partitioning_info["part_type"].values() and partitioning_info["swapfile_size"]:
        print_step(_("Creation and activation of the swapfile..."), clear=False)
        if partitioning_info["part_format_type"][partitioning_info["root_partition"]] == "btrfs":
            os.system(
                "btrfs subvolume create /mnt/swap && "
                "cd /mnt/swap && "
                "truncate -s 0 ./swapfile && "
                "chattr +C ./swapfile && "
                "btrfs property set ./swapfile compression none && "
                "cd -")
        else:
            os.system("mkdir -p /mnt/swap")
        os.system(f'fallocate -l "{partitioning_info["swapfile_size"]}" /mnt/swap/swapfile')
        os.system('chmod 600 /mnt/swap/swapfile')
        os.system('mkswap /mnt/swap/swapfile')
        os.system('swapon /mnt/swap/swapfile')

    print_step(_("Generating fstab..."), clear=False)
    os.system('genfstab -U /mnt >>/mnt/etc/fstab')

    print_step(_("Network configuration..."), clear=False)
    os.system('arch-chroot /mnt bash -c "systemctl enable NetworkManager"')
    os.system('arch-chroot /mnt bash -c "systemctl enable systemd-timesyncd"')

    if system_info["bootloader"]:
        print_step(_("Installation and configuration of the grub..."), clear=False)
        system_info["bootloader"].configure(system_info, pre_launch_info, partitioning_info)

    print_step(_("Users configuration..."), clear=False)
    print_sub_step(_("Root account configuration..."))
    if system_info["root_password"] != "":
        os.system(f'arch-chroot /mnt bash -c "echo \'root:{system_info["root_password"]}\' | chpasswd"')
    if system_info["user_name"] != "":
        print_sub_step(_("%s account configuration...") % system_info["user_name"])
        os.system('sed -i "s|# %wheel ALL=(ALL:ALL) ALL|%wheel ALL=(ALL:ALL) ALL|g" /mnt/etc/sudoers')
        os.system(
            f'arch-chroot /mnt bash -c "useradd --shell=/bin/bash --groups=wheel '
            f'--create-home {system_info["user_name"]}"')
        if system_info["user_full_name"] != "":
            os.system(
                f'arch-chroot /mnt bash -c "chfn -f \'{system_info["user_full_name"]}\' {system_info["user_name"]}"')
        if system_info["user_password"] != "":
            os.system(
                f'arch-chroot /mnt bash -c "echo \'{system_info["user_name"]}:'
                f'{system_info["user_password"]}\' | chpasswd"')

    print_step(_("Extra packages configuration if needed..."), clear=False)
    for bundle in system_info["bundles"]:
        bundle.configure(system_info, pre_launch_info, partitioning_info)

    umount_partitions()

    print_step(_("Installation complete ! You can reboot your system."), clear=False)


def pre_launch_steps() -> {}:
    """
    The method to proceed to the pre-launch steps
    :return:
    """
    print_step(_("Running pre-launch steps : "), clear=False)
    os.system('sed -i "s|#Color|Color|g" /etc/pacman.conf')
    os.system('sed -i "s|#ParallelDownloads = 5|ParallelDownloads = 5\\nDisableDownloadTimeout|g" /etc/pacman.conf')
    print_sub_step(_("Synchronising repositories and keyring..."))
    os.system("pacman --noconfirm -Sy --needed archlinux-keyring &>/dev/null")
    print_sub_step(_("Downloading and formatting translations..."))
    if not os.path.exists("fr.po"):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/rawleenc/ArchCraftsman/dev/locales/fr.po",
                                   "fr.po")
    os.system('msgfmt -o /usr/share/locale/fr/LC_MESSAGES/ArchCraftsman.mo fr.po &>/dev/null')
    print_sub_step(_("Querying IP geolocation informations..."))
    with urllib.request.urlopen('https://ipapi.co/json') as response:
        geoip_info = json.loads(response.read())
    detected_language = str(geoip_info["languages"]).split(",", maxsplit=1)[0]
    detected_timezone = geoip_info["timezone"]
    pre_launch_info = environment_config(detected_language)
    pre_launch_info["detected_timezone"] = detected_timezone
    pre_launch_info["live_console_font"] = locale_setup(keymap=pre_launch_info["keymap"],
                                                        global_language=pre_launch_info["global_language"])
    return pre_launch_info


if __name__ == '__main__':
    _ = gettext.gettext
    try:
        PRE_LAUNCH_INFO = pre_launch_steps()
        if PRE_LAUNCH_INFO["global_language"] != "EN":
            translation = gettext.translation('ArchCraftsman', localedir='/usr/share/locale',
                                              languages=[PRE_LAUNCH_INFO["global_language"].lower()])
            translation.install()
            _ = translation.gettext
        main(PRE_LAUNCH_INFO)
    except KeyboardInterrupt:
        print_error(_("Script execution interrupted by the user !"), do_pause=False)
        umount_partitions()
    except subprocess.CalledProcessError:
        print_error(_("A subprocess execution failed !"), do_pause=False)
        umount_partitions()
