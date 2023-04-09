# ArchCraftsman, The careful yet very fast Arch Linux Craftsman.
# Copyright (C) 2023 Rawleenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
The ArchCraftsman installer.
"""
import argparse
import readline
import sys
from subprocess import CalledProcessError

from archcraftsman.autopart import auto_partitioning
from archcraftsman.basesetup import pre_launch, setup_system
from archcraftsman.globalargs import GlobalArgs
from archcraftsman.globalinfo import GlobalInfo
from archcraftsman.i18n import I18n
from archcraftsman.manualpart import manual_partitioning
from archcraftsman.options import Desktops, FSFormats, Languages, PartTypes
from archcraftsman.shell import shell
from archcraftsman.utils import (
    execute,
    glob_completer,
    print_error,
    print_step,
    print_sub_step,
    prompt_bool,
)

_ = I18n().gettext


def install():
    """
    The main installation method.
    """
    try:
        if not GlobalArgs().config():
            setup_system()

        partitioning_info_ok: bool = bool(GlobalArgs().config())
        while not partitioning_info_ok:
            print_step(_("Partitioning :"))
            want_auto_part = prompt_bool(
                _("Do you want an automatic partitioning ?"), default=False
            )
            if want_auto_part:
                partitioning_info_ok = auto_partitioning()
            else:
                partitioning_info_ok = manual_partitioning()

        GlobalInfo().partitioning_info.format_and_mount_partitions()

        print_step(_("Updating mirrors..."), clear=False)
        execute(
            "reflector --verbose -phttps -f10 -l10 --sort rate -a2 --save /etc/pacman.d/mirrorlist"
        )

        base_pkgs = set()
        base_pkgs.update(["base", "base-devel", "linux-firmware"])

        base_pkgs.update(GlobalInfo().system_info.kernel().packages())

        pkgs = set()
        pkgs.update(
            [
                "man-db",
                "man-pages",
                "texinfo",
                "nano",
                "vim",
                "git",
                "curl",
                "os-prober",
                "efibootmgr",
                "xdg-user-dirs",
                "reflector",
                "numlockx",
                "net-tools",
                "polkit",
                "pacman-contrib",
            ]
        )

        if GlobalInfo().pre_launch_info.global_language.lower() != "en" and execute(
            f"pacman -Si man-pages-{GlobalInfo().pre_launch_info.global_language.lower()} &>/dev/null",
            check=False,
        ):
            pkgs.add(
                f"man-pages-{GlobalInfo().pre_launch_info.global_language.lower()}"
            )

        if GlobalInfo().partitioning_info.btrfs_in_use:
            pkgs.add("btrfs-progs")

        for bundle in GlobalInfo().system_info.bundles:
            pkgs.update(bundle.packages())

        if len(GlobalInfo().system_info.more_pkgs) > 0:
            pkgs.update(GlobalInfo().system_info.more_pkgs)

        print_step(_("Installation of the base..."), clear=False)
        execute(f'pacstrap -K /mnt {" ".join(base_pkgs)}')

        print_step(_("System configuration..."), clear=False)
        execute('sed -i "s|#en_US.UTF-8 UTF-8|en_US.UTF-8 UTF-8|g" /mnt/etc/locale.gen')
        execute('sed -i "s|#en_US ISO-8859-1|en_US ISO-8859-1|g" /mnt/etc/locale.gen')
        if GlobalInfo().pre_launch_info.global_language == Languages.FRENCH:
            execute(
                'sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /mnt/etc/locale.gen'
            )
            execute(
                'sed -i "s|#fr_FR ISO-8859-1|fr_FR ISO-8859-1|g" /mnt/etc/locale.gen'
            )
            execute('echo "LANG=fr_FR.UTF-8" >/mnt/etc/locale.conf')
        else:
            execute('echo "LANG=en_US.UTF-8" >/mnt/etc/locale.conf')
        execute(
            f'echo "KEYMAP={GlobalInfo().pre_launch_info.keymap}" >/mnt/etc/vconsole.conf'
        )
        execute(f'echo "{GlobalInfo().system_info.hostname}" >/mnt/etc/hostname')
        execute(
            f"""
            {{
                echo "127.0.0.1 localhost"
                echo "::1 localhost"
                echo "127.0.1.1 {GlobalInfo().system_info.hostname}.localdomain {GlobalInfo().system_info.hostname}"
            }} >>/mnt/etc/hosts
        """
        )
        execute("cp /etc/pacman.d/mirrorlist /mnt/etc/pacman.d/mirrorlist")

        print_step(_("Locales configuration..."), clear=False)
        execute(
            f'arch-chroot /mnt bash -c "ln -sf {GlobalInfo().system_info.timezone} /etc/localtime"'
        )
        execute('arch-chroot /mnt bash -c "locale-gen"')

        print_step(_("Installation of the remaining packages..."), clear=False)
        execute('sed -i "s|#Color|Color|g" /mnt/etc/pacman.conf')
        execute(
            'sed -i "s|#ParallelDownloads = 5|ParallelDownloads = 5\\nDisableDownloadTimeout|g" /mnt/etc/pacman.conf'
        )
        execute('arch-chroot /mnt bash -c "pacman --noconfirm -Sy archlinux-keyring"')
        execute('arch-chroot /mnt bash -c "pacman --noconfirm -Su"')
        execute(f'arch-chroot /mnt bash -c "pacman --noconfirm -S {" ".join(pkgs)}"')

        if (
            PartTypes.SWAP
            not in [
                part.part_type for part in GlobalInfo().partitioning_info.partitions
            ]
            and GlobalInfo().partitioning_info.swapfile_size
        ):
            print_step(_("Creation and activation of the swapfile..."), clear=False)
            if (
                GlobalInfo().partitioning_info.root_partition().part_format_type
                == FSFormats.BTRFS
            ):
                execute(
                    "btrfs subvolume create /mnt/swap && "
                    "cd /mnt/swap && "
                    "truncate -s 0 ./swapfile && "
                    "chattr +C ./swapfile && "
                    "btrfs property set ./swapfile compression none && "
                    "cd -"
                )
            else:
                execute("mkdir -p /mnt/swap")
            execute(
                f'fallocate -l "{GlobalInfo().partitioning_info.swapfile_size}" /mnt/swap/swapfile'
            )
            execute("chmod 600 /mnt/swap/swapfile")
            execute("mkswap /mnt/swap/swapfile")
            execute("swapon /mnt/swap/swapfile")

        print_step(_("Generating fstab..."), clear=False)
        execute("genfstab -U /mnt >>/mnt/etc/fstab")

        if GlobalInfo().system_info.desktop().name != Desktops.NONE:
            print_step(_("Desktop configuration..."), clear=False)
            GlobalInfo().system_info.desktop().configure()

        print_step(_("Network configuration..."), clear=False)
        GlobalInfo().system_info.network().configure()

        execute('arch-chroot /mnt bash -c "systemctl enable systemd-timesyncd"')

        print_step(_("Installation and configuration of the grub..."), clear=False)
        GlobalInfo().system_info.bootloader().configure()

        print_step(_("Users configuration..."), clear=False)
        print_sub_step(_("Root account configuration..."))
        if GlobalInfo().system_info.root_password:
            execute(
                f"arch-chroot /mnt bash -c \"echo 'root:{GlobalInfo().system_info.root_password}' | chpasswd\""
            )
        if GlobalInfo().system_info.user_name:
            print_sub_step(
                _("%s account configuration...") % GlobalInfo().system_info.user_name
            )
            execute(
                'sed -i "s|# %wheel ALL=(ALL:ALL) ALL|%wheel ALL=(ALL:ALL) ALL|g" /mnt/etc/sudoers'
            )
            execute(
                f'arch-chroot /mnt bash -c "useradd --shell=/bin/bash --groups=wheel '
                f'--create-home {GlobalInfo().system_info.user_name}"'
            )
            if GlobalInfo().system_info.user_full_name:
                execute(
                    f"arch-chroot /mnt bash -c "
                    f"\"chfn -f '{GlobalInfo().system_info.user_full_name}' {GlobalInfo().system_info.user_name}\""
                )
            if GlobalInfo().system_info.user_password:
                execute(
                    f"arch-chroot /mnt bash -c \"echo '{GlobalInfo().system_info.user_name}:"
                    f"{GlobalInfo().system_info.user_password}' | chpasswd\""
                )

        print_step(_("Extra packages configuration if needed..."), clear=False)
        for bundle in GlobalInfo().system_info.others():
            bundle.configure()

        GlobalInfo().serialize()
        GlobalInfo().partitioning_info.umount_partitions()

        print_step(
            _("Installation complete ! You can reboot your system."), clear=False
        )

    except KeyboardInterrupt:
        print_error(_("Script execution interrupted by the user !"), do_pause=False)
        GlobalInfo().serialize()
        GlobalInfo().partitioning_info.umount_partitions()
        sys.exit(1)
    except CalledProcessError as exception:
        print_error(
            _("A subprocess execution failed ! See the following error: %s")
            % exception,
            do_pause=False,
        )
        GlobalInfo().serialize()
        GlobalInfo().partitioning_info.umount_partitions()
        sys.exit(1)
    except EOFError:
        sys.exit(1)


def main():
    """
    The main installer method.
    """
    parser = argparse.ArgumentParser(description="The ArchCraftsman installer.")
    parser.add_argument(
        "-i",
        "--install",
        action="store_const",
        const=True,
        default=False,
        help="Process to ArchLinux installation. Must be used in a live environment.",
    )
    parser.add_argument(
        "-s",
        "--shell",
        action="store_const",
        const=True,
        default=False,
        help="Start ArchCraftsman in interactive shell mode. Useless if used with --install.",
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        help="Used to specify a config file to use. Can be used with both --install and --shell.",
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_const",
        const=True,
        default=False,
        help="Used to test the installer. No destructive commands will be executed.",
    )
    GlobalArgs(parser.parse_args())

    readline.set_completer_delims(" \t\n;")
    readline.parse_and_bind("tab: complete")
    readline.set_completer(glob_completer)

    if not GlobalArgs().is_call_ok():
        parser.print_help()
        sys.exit(1)

    if GlobalArgs().install():
        pre_launch()
        I18n().update_method(GlobalInfo().pre_launch_info.global_language)
        install()
        sys.exit(0)

    if GlobalArgs().shell():
        pre_launch(shell_mode=True)
        I18n().update_method(GlobalInfo().pre_launch_info.global_language)
        shell()
        sys.exit(0)


if __name__ == "__main__":
    main()
