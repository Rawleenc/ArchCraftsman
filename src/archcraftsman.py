"""
LICENSE
ArchCraftsman, The careful yet very fast Arch Linux Craftsman.
Copyright (C) 2022  Rawleenc

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
import argparse
import glob
import json
import re
import urllib.request
from subprocess import CalledProcessError

import readline

from src.autopart import auto_partitioning
from src.envsetup import setup_environment
from src.globalargs import GlobalArgs
from src.i18n import I18n
from src.localesetup import setup_locale
from src.manualpart import manual_partitioning
from src.options import PartType, FSFormat
from src.systemsetup import setup_system
from src.utils import is_bios, format_partition, print_error, print_step, print_sub_step, prompt_bool, execute, stdout


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
    swap = re.sub('\\s', '', stdout(execute('swapon --noheadings | awk \'{print $1}\'', capture_output=True)))
    if swap != "":
        execute(f'swapoff {swap} &>/dev/null')

    execute('umount -R /mnt &>/dev/null')


def main(pre_launch_info):
    """ The main method. """
    system_info = setup_system(pre_launch_info["detected_timezone"])
    btrfs_in_use = False

    partitioning_info = None
    while partitioning_info is None:
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
    if partitioning_info["part_format_type"][partitioning_info["root_partition"]] == FSFormat.BTRFS:
        btrfs_in_use = True

    for partition in partitioning_info["partitions"]:
        if partitioning_info["part_format_type"].get(partition) == FSFormat.BTRFS:
            btrfs_in_use = True
        if not is_bios() and partitioning_info["part_type"].get(partition) == PartType.EFI:
            format_partition(partition, partitioning_info["part_format_type"].get(partition),
                             partitioning_info["part_mount_point"].get(partition),
                             partitioning_info["part_format"].get(partition))
        elif partitioning_info["part_type"].get(partition) == PartType.HOME:
            format_partition(partition, partitioning_info["part_format_type"].get(partition),
                             partitioning_info["part_mount_point"].get(partition),
                             partitioning_info["part_format"].get(partition))
        elif partitioning_info["part_type"].get(partition) == PartType.SWAP:
            execute(f'mkswap "{partition}"')
            execute(f'swapon "{partition}"')
        elif partitioning_info["part_type"].get(partition) == PartType.OTHER:
            format_partition(partition, partitioning_info["part_format_type"].get(partition),
                             partitioning_info["part_mount_point"].get(partition),
                             partitioning_info["part_format"].get(partition))

    print_step(_("Updating mirrors..."), clear=False)
    execute('reflector --verbose -phttps -f10 -l10 --sort rate -a2 --save /etc/pacman.d/mirrorlist')

    base_pkgs = set()
    base_pkgs.update(["base", "base-devel", "linux-firmware"])

    if system_info["kernel"]:
        base_pkgs.update(system_info["kernel"].packages(system_info))

    pkgs = set()
    pkgs.update(["man-db", "man-pages", "texinfo", "nano", "vim", "git", "curl", "os-prober", "efibootmgr",
                 "networkmanager", "xdg-user-dirs", "reflector", "numlockx", "net-tools", "polkit", "pacman-contrib"])

    if pre_launch_info["global_language"].lower() != "en" and execute(
            f"pacman -Si man-pages-{pre_launch_info['global_language'].lower()} &>/dev/null").returncode == 0:
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
    execute(f'pacstrap -K /mnt {" ".join(base_pkgs)}')

    print_step(_("System configuration..."), clear=False)
    execute('sed -i "s|#en_US.UTF-8 UTF-8|en_US.UTF-8 UTF-8|g" /mnt/etc/locale.gen')
    execute('sed -i "s|#en_US ISO-8859-1|en_US ISO-8859-1|g" /mnt/etc/locale.gen')
    if pre_launch_info["global_language"] == "FR":
        execute('sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /mnt/etc/locale.gen')
        execute('sed -i "s|#fr_FR ISO-8859-1|fr_FR ISO-8859-1|g" /mnt/etc/locale.gen')
        execute('echo "LANG=fr_FR.UTF-8" >/mnt/etc/locale.conf')
    else:
        execute('echo "LANG=en_US.UTF-8" >/mnt/etc/locale.conf')
    execute(f'echo "KEYMAP={pre_launch_info["keymap"]}" >/mnt/etc/vconsole.conf')
    execute(f'echo "{system_info["hostname"]}" >/mnt/etc/hostname')
    execute(f'''
        {{
            echo "127.0.0.1 localhost"
            echo "::1 localhost"
            echo "127.0.1.1 {system_info["hostname"]}.localdomain {system_info["hostname"]}"
        }} >>/mnt/etc/hosts
    ''')
    execute('cp /etc/pacman.d/mirrorlist /mnt/etc/pacman.d/mirrorlist')

    print_step(_("Locales configuration..."), clear=False)
    execute(f'arch-chroot /mnt bash -c "ln -sf {system_info["timezone"]} /etc/localtime"')
    execute('arch-chroot /mnt bash -c "locale-gen"')

    print_step(_("Installation of the remaining packages..."), clear=False)
    execute('sed -i "s|#Color|Color|g" /mnt/etc/pacman.conf')
    execute('sed -i "s|#ParallelDownloads = 5|ParallelDownloads = 5\\nDisableDownloadTimeout|g" /mnt/etc/pacman.conf')
    execute('arch-chroot /mnt bash -c "pacman --noconfirm -Sy archlinux-keyring"')
    execute('arch-chroot /mnt bash -c "pacman --noconfirm -Su"')
    execute(f'arch-chroot /mnt bash -c "pacman --noconfirm -S {" ".join(pkgs)}"')

    if PartType.SWAP not in partitioning_info["part_type"].values() and partitioning_info["swapfile_size"]:
        print_step(_("Creation and activation of the swapfile..."), clear=False)
        if partitioning_info["part_format_type"][partitioning_info["root_partition"]] == FSFormat.BTRFS:
            execute(
                "btrfs subvolume create /mnt/swap && "
                "cd /mnt/swap && "
                "truncate -s 0 ./swapfile && "
                "chattr +C ./swapfile && "
                "btrfs property set ./swapfile compression none && "
                "cd -")
        else:
            execute("mkdir -p /mnt/swap")
        execute(f'fallocate -l "{partitioning_info["swapfile_size"]}" /mnt/swap/swapfile')
        execute('chmod 600 /mnt/swap/swapfile')
        execute('mkswap /mnt/swap/swapfile')
        execute('swapon /mnt/swap/swapfile')

    print_step(_("Generating fstab..."), clear=False)
    execute('genfstab -U /mnt >>/mnt/etc/fstab')

    print_step(_("Network configuration..."), clear=False)
    execute('arch-chroot /mnt bash -c "systemctl enable NetworkManager"')
    execute('arch-chroot /mnt bash -c "systemctl enable systemd-timesyncd"')

    if system_info["bootloader"]:
        print_step(_("Installation and configuration of the grub..."), clear=False)
        system_info["bootloader"].configure(system_info, pre_launch_info, partitioning_info)

    print_step(_("Users configuration..."), clear=False)
    print_sub_step(_("Root account configuration..."))
    if system_info["root_password"] != "":
        execute(f'arch-chroot /mnt bash -c "echo \'root:{system_info["root_password"]}\' | chpasswd"')
    if system_info["user_name"] != "":
        print_sub_step(_("%s account configuration...") % system_info["user_name"])
        execute('sed -i "s|# %wheel ALL=(ALL:ALL) ALL|%wheel ALL=(ALL:ALL) ALL|g" /mnt/etc/sudoers')
        execute(
            f'arch-chroot /mnt bash -c "useradd --shell=/bin/bash --groups=wheel '
            f'--create-home {system_info["user_name"]}"')
        if system_info["user_full_name"] != "":
            execute(
                f'arch-chroot /mnt bash -c "chfn -f \'{system_info["user_full_name"]}\' {system_info["user_name"]}"')
        if system_info["user_password"] != "":
            execute(
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
    execute('sed -i "s|#Color|Color|g" /etc/pacman.conf')
    execute('sed -i "s|#ParallelDownloads = 5|ParallelDownloads = 5\\nDisableDownloadTimeout|g" /etc/pacman.conf')

    print_sub_step(_("Synchronising repositories and keyring..."))
    execute("pacman --noconfirm -Sy --needed archlinux-keyring &>/dev/null")

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
    parser = argparse.ArgumentParser(description="The ArchCraftsman installer.")
    parser.add_argument('-t', '--test', action='store_const', const=True, default=False,
                        help='Used to test the installer. No command will be executed.')
    args = parser.parse_args()

    i18n = I18n()
    _ = i18n.gettext
    GlobalArgs(args)

    user = stdout(execute("whoami", capture_output=True, force=True))
    if not user or user.strip() != "root":
        print_error("This script must be run as root.")
        exit(1)

    try:
        PRE_LAUNCH_INFO = pre_launch_steps()
        _ = i18n.update_method(PRE_LAUNCH_INFO["global_language"])
        main(PRE_LAUNCH_INFO)
    except KeyboardInterrupt:
        print_error(_("Script execution interrupted by the user !"), do_pause=False)
        umount_partitions()
    except CalledProcessError as e:
        print_error(_("A subprocess execution failed ! See the following error: %s") % e, do_pause=False)
        umount_partitions()
