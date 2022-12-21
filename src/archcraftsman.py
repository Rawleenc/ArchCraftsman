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
import gettext
import glob
import json
import os
import re
import subprocess
import urllib.request

import readline

from src.autopart import auto_partitioning
from src.i18n import I18n
from src.manualpart import manual_partitioning
from src.syssetup import setup_system
from src.envsetup import setup_environment
from src.localesetup import setup_locale
from src.utils import is_bios, format_partition, print_error, print_step, print_sub_step, prompt_bool


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


def umount_partitions():
    """
    A method to unmount all mounted partitions.
    """
    print_step(_("Unmounting partitions..."), clear=False)
    swap = re.sub('\\s', '', os.popen('swapon --noheadings | awk \'{print $1}\'').read())
    if swap != "":
        os.system(f'swapoff {swap} &>/dev/null')

    os.system('umount -R /mnt &>/dev/null')


def main(pre_launch_info):
    """ The main method. """
    system_info = setup_system(pre_launch_info["detected_timezone"])
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

    print_sub_step(_("Synchronising repositories..."))
    os.system("pacman -Sy &>/dev/null")

    print_sub_step(_("Querying IP geolocation informations..."))
    with urllib.request.urlopen('https://ipapi.co/json') as response:
        geoip_info = json.loads(response.read())
    detected_language = str(geoip_info["languages"]).split(",", maxsplit=1)[0]
    detected_timezone = geoip_info["timezone"]
    pre_launch_info = setup_environment(detected_language)
    pre_launch_info["detected_timezone"] = detected_timezone
    pre_launch_info["live_console_font"] = setup_locale(keymap=pre_launch_info["keymap"],
                                                        global_language=pre_launch_info["global_language"])
    return pre_launch_info


if __name__ == '__main__':
    i18n = I18n()
    _ = i18n.gettext
    try:
        PRE_LAUNCH_INFO = pre_launch_steps()
        if PRE_LAUNCH_INFO["global_language"] != "EN":
            translation = gettext.translation('ArchCraftsman', localedir='/usr/share/locale',
                                              languages=[PRE_LAUNCH_INFO["global_language"].lower()])
            translation.install()
            _ = i18n.update_method(translation.gettext)
        main(PRE_LAUNCH_INFO)
    except KeyboardInterrupt:
        print_error(_("Script execution interrupted by the user !"), do_pause=False)
        umount_partitions()
    except subprocess.CalledProcessError:
        print_error(_("A subprocess execution failed !"), do_pause=False)
        umount_partitions()
