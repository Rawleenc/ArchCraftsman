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
import subprocess
import sys

import archcraftsman.arguments
import archcraftsman.autopart
import archcraftsman.base
import archcraftsman.basesetup
import archcraftsman.btrfs
import archcraftsman.config
import archcraftsman.i18n
import archcraftsman.info
import archcraftsman.manualpart
import archcraftsman.options
import archcraftsman.shell
import archcraftsman.utils

_ = archcraftsman.i18n.translate


def update_mirrorlist():
    """
    Update the mirrorlist.
    """
    config: bool = bool(archcraftsman.arguments.config())
    user_answer = False
    manual_change = False
    while not user_answer:
        if not manual_change:
            archcraftsman.base.print_step(_("Updating mirrors..."), clear=not config)
            archcraftsman.base.update_mirrors()
        else:
            manual_change = False
        if config:
            user_answer = True
            break
        archcraftsman.base.print_step(_("Current mirrorlist :"))
        archcraftsman.base.execute("cat /etc/pacman.d/mirrorlist")
        user_answer = archcraftsman.utils.prompt_bool(
            _("Are you satisfied with the mirrors ?"), default=True
        )
        if not user_answer:
            if archcraftsman.utils.prompt_bool(
                _("Do you want to manually edit the mirrorlist ?"), default=True
            ):
                archcraftsman.base.execute("nano /etc/pacman.d/mirrorlist")
                manual_change = True


def install():
    """
    The main installation method.
    """
    try:
        if not archcraftsman.arguments.config():
            archcraftsman.basesetup.setup_system()

        partitioning_info_ok: bool = bool(archcraftsman.arguments.config())
        while not partitioning_info_ok:
            archcraftsman.base.print_step(_("Partitioning :"))
            want_auto_part = archcraftsman.utils.prompt_bool(
                _("Do you want an automatic partitioning ?"), default=False
            )
            if want_auto_part:
                partitioning_info_ok = archcraftsman.autopart.auto_partitioning()
            else:
                partitioning_info_ok = archcraftsman.manualpart.manual_partitioning()

        archcraftsman.info.ai.partitioning_info.format_and_mount_partitions()

        update_mirrorlist()

        base_pkgs = set()
        base_pkgs.update(["base", "base-devel", "linux-firmware"])

        base_pkgs.update(archcraftsman.info.ai.system_info.kernel().packages())

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

        if archcraftsman.info.ai.pre_launch_info.global_language.lower() != "en" and archcraftsman.base.execute(
            f"pacman -Si man-pages-{archcraftsman.info.ai.pre_launch_info.global_language.lower()} &>/dev/null",
            check=False,
        ):
            pkgs.add(
                f"man-pages-{archcraftsman.info.ai.pre_launch_info.global_language.lower()}"
            )

        if (
            archcraftsman.info.ai.partitioning_info.root_partition().part_format
            == archcraftsman.options.FSFormats.BTRFS
        ):
            pkgs.update(archcraftsman.btrfs.get_management_packages())
        elif (
            archcraftsman.info.ai.partitioning_info.filesystem_in_use()
            == archcraftsman.options.FSFormats.BTRFS
        ):
            pkgs.update(archcraftsman.btrfs.get_packages())

        for bundle in archcraftsman.info.ai.system_info.bundles:
            pkgs.update(bundle.packages())

        if len(archcraftsman.info.ai.system_info.more_pkgs) > 0:
            pkgs.update(archcraftsman.info.ai.system_info.more_pkgs)

        archcraftsman.base.print_step(_("Installation of the base..."), clear=False)
        archcraftsman.base.execute(f'pacstrap -K /mnt {" ".join(base_pkgs)}')

        archcraftsman.base.print_step(_("System configuration..."), clear=False)
        archcraftsman.base.execute(
            'sed -i "s|#en_US.UTF-8 UTF-8|en_US.UTF-8 UTF-8|g" /mnt/etc/locale.gen'
        )
        archcraftsman.base.execute(
            'sed -i "s|#en_US ISO-8859-1|en_US ISO-8859-1|g" /mnt/etc/locale.gen'
        )
        if (
            archcraftsman.info.ai.pre_launch_info.global_language
            == archcraftsman.options.Languages.FRENCH
        ):
            archcraftsman.base.execute(
                'sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /mnt/etc/locale.gen'
            )
            archcraftsman.base.execute(
                'sed -i "s|#fr_FR ISO-8859-1|fr_FR ISO-8859-1|g" /mnt/etc/locale.gen'
            )
            archcraftsman.base.execute('echo "LANG=fr_FR.UTF-8" >/mnt/etc/locale.conf')
        else:
            archcraftsman.base.execute('echo "LANG=en_US.UTF-8" >/mnt/etc/locale.conf')
        archcraftsman.base.execute(
            f'echo "KEYMAP={archcraftsman.info.ai.pre_launch_info.keymap}" >/mnt/etc/vconsole.conf'
        )
        _hostname = archcraftsman.info.ai.system_info.hostname
        archcraftsman.base.execute(f'echo "{_hostname}" >/mnt/etc/hostname')
        archcraftsman.base.execute(
            f"""
            {{
                echo "127.0.0.1 localhost"
                echo "::1 localhost"
                echo "127.0.1.1 {_hostname}.localdomain {_hostname}"
            }} >>/mnt/etc/hosts
            """
        )
        archcraftsman.base.execute(
            "cp /etc/pacman.d/mirrorlist /mnt/etc/pacman.d/mirrorlist"
        )

        archcraftsman.base.print_step(_("Locales configuration..."), clear=False)
        archcraftsman.base.execute(
            f"ln -sf {archcraftsman.info.ai.system_info.timezone} /etc/localtime",
            chroot=True,
        )
        archcraftsman.base.execute("locale-gen", chroot=True)

        archcraftsman.base.print_step(
            _("Installation of the remaining packages..."), clear=False
        )
        archcraftsman.base.execute('sed -i "s|#Color|Color|g" /mnt/etc/pacman.conf')
        archcraftsman.base.execute(
            'sed -i "s|#ParallelDownloads = 5|ParallelDownloads = 5\\nDisableDownloadTimeout|g" /mnt/etc/pacman.conf'
        )
        archcraftsman.base.execute(
            "pacman --noconfirm -Sy archlinux-keyring", chroot=True
        )
        archcraftsman.base.execute("pacman --noconfirm -Su", chroot=True)
        archcraftsman.base.execute(
            f'pacman --noconfirm -S {" ".join(pkgs)}', chroot=True
        )

        if (
            archcraftsman.options.PartTypes.SWAP
            not in [
                part.part_type
                for part in archcraftsman.info.ai.partitioning_info.partitions
            ]
            and archcraftsman.info.ai.partitioning_info.swapfile_size
        ):
            archcraftsman.base.print_step(
                _("Creation and activation of the swapfile..."), clear=False
            )
            archcraftsman.base.execute("mkdir -p /mnt/swap")
            archcraftsman.base.execute(
                f'fallocate -l "{archcraftsman.info.ai.partitioning_info.swapfile_size}" /mnt/swap/swapfile'
            )
            archcraftsman.base.execute("chmod 600 /mnt/swap/swapfile")
            archcraftsman.base.execute("mkswap /mnt/swap/swapfile")
            archcraftsman.base.execute("swapon /mnt/swap/swapfile")

        if (
            archcraftsman.info.ai.system_info.desktop().name
            != archcraftsman.options.Desktops.NONE
        ):
            archcraftsman.base.print_step(_("Desktop configuration..."), clear=False)
            archcraftsman.info.ai.system_info.desktop().configure()

        archcraftsman.base.print_step(_("Network configuration..."), clear=False)
        archcraftsman.info.ai.system_info.network().configure()

        archcraftsman.base.execute("systemctl enable systemd-timesyncd", chroot=True)

        archcraftsman.base.print_step(
            _("Installation and configuration of the grub..."), clear=False
        )
        archcraftsman.info.ai.system_info.bootloader().configure()

        archcraftsman.base.print_step(_("Users configuration..."), clear=False)
        archcraftsman.base.print_sub_step(_("Root account configuration..."))
        if archcraftsman.info.ai.system_info.root_password:
            archcraftsman.base.execute(
                f"echo 'root:{archcraftsman.info.ai.system_info.root_password}' | chpasswd",
                chroot=True,
            )
        if archcraftsman.info.ai.system_info.user_name:
            archcraftsman.base.print_sub_step(
                _("%s account configuration...")
                % archcraftsman.info.ai.system_info.user_name
            )
            archcraftsman.base.execute(
                'sed -i "s|# %wheel ALL=(ALL:ALL) ALL|%wheel ALL=(ALL:ALL) ALL|g" /mnt/etc/sudoers'
            )
            archcraftsman.base.execute(
                f"useradd --shell=/bin/bash --groups=wheel "
                f"--create-home {archcraftsman.info.ai.system_info.user_name}",
                chroot=True,
            )
            if archcraftsman.info.ai.system_info.user_full_name:
                archcraftsman.base.execute(
                    f"chfn -f '{archcraftsman.info.ai.system_info.user_full_name}' "
                    f"{archcraftsman.info.ai.system_info.user_name}",
                    chroot=True,
                )
            if archcraftsman.info.ai.system_info.user_password:
                archcraftsman.base.execute(
                    f"echo '{archcraftsman.info.ai.system_info.user_name}:"
                    f"{archcraftsman.info.ai.system_info.user_password}' | chpasswd",
                    chroot=True,
                )

        archcraftsman.base.print_step(
            _("Extra packages configuration if needed..."), clear=False
        )
        for bundle in archcraftsman.info.ai.system_info.others():
            bundle.configure()

        if (
            archcraftsman.info.ai.partitioning_info.root_partition().part_format_type
            == archcraftsman.options.FSFormats.BTRFS
        ):
            archcraftsman.base.print_step(_("BTRFS configuration..."), clear=False)
            archcraftsman.btrfs.configure(
                archcraftsman.info.ai.partitioning_info.root_partition().real_path()
            )

        archcraftsman.base.print_step(_("Generating fstab..."), clear=False)
        archcraftsman.base.execute("genfstab -U /mnt >>/mnt/etc/fstab")

        archcraftsman.config.serialize()
        archcraftsman.info.ai.partitioning_info.umount_partitions()

        archcraftsman.base.print_step(
            _("Installation complete ! You can reboot your system."), clear=False
        )

    except KeyboardInterrupt:
        archcraftsman.base.print_error(
            _("Script execution interrupted by the user !"), do_pause=False
        )
        archcraftsman.config.serialize()
        archcraftsman.info.ai.partitioning_info.umount_partitions()
        sys.exit(1)
    except subprocess.CalledProcessError as exception:
        archcraftsman.base.print_error(
            _("A subprocess execution failed ! See the following error: %s")
            % exception,
            do_pause=False,
        )
        archcraftsman.config.serialize()
        archcraftsman.info.ai.partitioning_info.umount_partitions()
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
    archcraftsman.arguments.init(parser.parse_args())

    readline.set_completer_delims(" \t\n;")
    readline.parse_and_bind("tab: complete")
    readline.set_completer(archcraftsman.base.glob_completer)

    if not archcraftsman.arguments.is_call_ok():
        parser.print_help()
        sys.exit(1)

    if archcraftsman.arguments.install():
        archcraftsman.basesetup.pre_launch()
        archcraftsman.i18n.update_method(
            archcraftsman.info.ai.pre_launch_info.global_language
        )
        install()
        sys.exit(0)

    if archcraftsman.arguments.shell():
        archcraftsman.basesetup.pre_launch(shell_mode=True)
        archcraftsman.i18n.update_method(
            archcraftsman.info.ai.pre_launch_info.global_language
        )
        archcraftsman.shell.shell()
        sys.exit(0)


if __name__ == "__main__":
    main()
