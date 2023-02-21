"""
The installer mode module
"""
import re
import sys
from subprocess import CalledProcessError

from src.autopart import auto_partitioning
from src.i18n import I18n
from src.manualpart import manual_partitioning
from src.options import FSFormats, PartTypes
from src.partitioninginfo import PartitioningInfo
from src.systemsetup import setup_system
from src.utils import print_step, stdout, execute, prompt_bool, print_sub_step, print_error

_ = I18n().gettext


def umount_partitions(partitioning_info: PartitioningInfo):
    """
    A method to unmount all mounted partitions.
    """
    print_step(_("Unmounting partitions..."), clear=False)
    swap = re.sub('\\s', '',
                  stdout(execute('swapon --noheadings | awk \'{print $1}\'', check=False, capture_output=True)))
    if swap != "":
        execute(f'swapoff {swap} &>/dev/null', check=False)

    mounted_partitions = [partition for partition in partitioning_info.partitions if
                          partition.part_mounted and partition.part_type != PartTypes.ROOT]
    mounted_partitions.sort(key=lambda partition: len(partition.part_mount_point), reverse=True)

    while True in [partition.part_mounted for partition in mounted_partitions]:
        for partition in [partition for partition in mounted_partitions if partition.part_mounted]:
            partition.umount()
    partitioning_info.root_partition.umount()


def install(pre_launch_info):
    """
    The main installation method.
    :param pre_launch_info:
    :return:
    """
    partitioning_info: PartitioningInfo = PartitioningInfo()
    try:
        system_info = setup_system(pre_launch_info["detected_timezone"])
        btrfs_in_use = False

        temp_partitioning_info = None
        while temp_partitioning_info is None:
            print_step(_("Partitioning :"))
            want_auto_part = prompt_bool(_("Do you want an automatic partitioning ? (y/N) : "), default=False)
            if want_auto_part:
                temp_partitioning_info = auto_partitioning()
            else:
                temp_partitioning_info = manual_partitioning()
        partitioning_info: PartitioningInfo = temp_partitioning_info

        print_step(_("Formatting and mounting partitions..."), clear=False)

        for partition in partitioning_info.partitions:
            if partition.part_format_type == FSFormats.BTRFS:
                btrfs_in_use = True
            print_sub_step(_("Formatting %s...") % (partition.real_path()))
            partition.format_partition()

        if partitioning_info.root_partition.part_format_type == FSFormats.BTRFS:
            btrfs_in_use = True
        print_sub_step(_("Mounting %s...") % (partitioning_info.root_partition.real_path()))
        partitioning_info.root_partition.mount()

        for partition in [partition for partition in partitioning_info.partitions if not partition.part_mounted]:
            if partition.part_format_type == FSFormats.BTRFS:
                btrfs_in_use = True
            print_sub_step(_("Mounting %s...") % (partition.real_path()))
            partition.mount()

        print_step(_("Updating mirrors..."), clear=False)
        execute('reflector --verbose -phttps -f10 -l10 --sort rate -a2 --save /etc/pacman.d/mirrorlist')

        base_pkgs = set()
        base_pkgs.update(["base", "base-devel", "linux-firmware"])

        if system_info["kernel"]:
            base_pkgs.update(system_info["kernel"].packages(system_info))

        pkgs = set()
        pkgs.update(["man-db", "man-pages", "texinfo", "nano", "vim", "git", "curl", "os-prober", "efibootmgr",
                     "networkmanager", "xdg-user-dirs", "reflector", "numlockx", "net-tools", "polkit",
                     "pacman-contrib"])

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
        execute(
            'sed -i "s|#ParallelDownloads = 5|ParallelDownloads = 5\\nDisableDownloadTimeout|g" /mnt/etc/pacman.conf')
        execute('arch-chroot /mnt bash -c "pacman --noconfirm -Sy archlinux-keyring"')
        execute('arch-chroot /mnt bash -c "pacman --noconfirm -Su"')
        execute(f'arch-chroot /mnt bash -c "pacman --noconfirm -S {" ".join(pkgs)}"')

        if PartTypes.SWAP not in [part.part_type for part in
                                  partitioning_info.partitions] and partitioning_info.swapfile_size:
            print_step(_("Creation and activation of the swapfile..."), clear=False)
            if partitioning_info.root_partition.part_format_type == FSFormats.BTRFS:
                execute(
                    "btrfs subvolume create /mnt/swap && "
                    "cd /mnt/swap && "
                    "truncate -s 0 ./swapfile && "
                    "chattr +C ./swapfile && "
                    "btrfs property set ./swapfile compression none && "
                    "cd -")
            else:
                execute("mkdir -p /mnt/swap")
            execute(f'fallocate -l "{partitioning_info.swapfile_size}" /mnt/swap/swapfile')
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
                    f'arch-chroot /mnt bash -c '
                    f'"chfn -f \'{system_info["user_full_name"]}\' {system_info["user_name"]}"')
            if system_info["user_password"] != "":
                execute(
                    f'arch-chroot /mnt bash -c "echo \'{system_info["user_name"]}:'
                    f'{system_info["user_password"]}\' | chpasswd"')

        print_step(_("Extra packages configuration if needed..."), clear=False)
        for bundle in system_info["bundles"]:
            bundle.configure(system_info, pre_launch_info, partitioning_info)

        umount_partitions(partitioning_info)

        print_step(_("Installation complete ! You can reboot your system."), clear=False)

    except KeyboardInterrupt:
        print_error(_("Script execution interrupted by the user !"), do_pause=False)
        umount_partitions(partitioning_info)
        sys.exit(1)
    except CalledProcessError as exception:
        print_error(_("A subprocess execution failed ! See the following error: %s") % exception, do_pause=False)
        umount_partitions(partitioning_info)
        sys.exit(1)
    except EOFError:
        sys.exit(1)
