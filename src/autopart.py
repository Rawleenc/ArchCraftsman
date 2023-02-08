"""
The automatic partitioning system module
"""
import os

from src.disk import Disk
from src.i18n import I18n
from src.options import SwapTypes, PartTypes, FSFormats
from src.partition import Partition
from src.partitioninginfo import PartitioningInfo
from src.utils import ask_format_type, is_bios, from_iec, to_iec, print_error, print_step, print_sub_step, prompt, \
    prompt_bool, prompt_option, execute

_ = I18n().gettext


def auto_partitioning() -> PartitioningInfo or None:
    """
    The method to proceed to the automatic partitioning.
    :return:
    """
    partitioning_info = PartitioningInfo()
    user_answer = False
    while not user_answer:
        print_step(_("Automatic partitioning :"))
        execute("fdisk -l", force=True)
        target_disk = prompt(
            _("On which drive should Archlinux be installed ? (type the entire name, for example '/dev/sda') : "))
        if target_disk == "":
            print_error(_("You need to choose a target drive."))
            continue
        if not os.path.exists(target_disk):
            print_error(_("You need to choose a target drive."))
            continue
        partitioning_info.main_disk = target_disk
        disk = Disk(target_disk)
        efi_partition = disk.get_efi_partition()
        if not is_bios() \
                and len(disk.partitions) > 0 \
                and efi_partition.path != "" \
                and efi_partition.fs_type == "vfat" \
                and disk.free_space > from_iec("32G"):
            want_dual_boot = prompt_bool(_("Do you want to install Arch Linux next to other systems ? (Y/n) : "))
        else:
            want_dual_boot = False

        swap_type = prompt_option(_("What type of Swap do you want ? (%s) : "), _("Swap type '%s' is not supported."),
                                  SwapTypes, supported_msg=_("Supported Swap types : "), default=SwapTypes.FILE)

        want_home = prompt_bool(_("Do you want a separated Home ? (Y/n) : "))
        part_format_type = ask_format_type()
        root_block_name = None
        if prompt_bool(_("Do you want to encrypt the %s partition ? (y/N) : ") % "Root", default=False):
            root_block_name = "root"
        home_block_name = None
        if want_home:
            if prompt_bool(_("Do you want to encrypt the %s partition ? (y/N) : ") % "Home", default=False):
                home_block_name = "home"

        if want_dual_boot:
            root_size = to_iec(int(disk.free_space / 4))
            swap_size = to_iec(int(disk.free_space / 32))
        else:
            root_size = to_iec(int(disk.total / 4))
            swap_size = to_iec(int(disk.total / 32))
        if swap_type == SwapTypes.NONE:
            swap_size = None
        elif swap_type == SwapTypes.FILE:
            partitioning_info.swapfile_size = swap_size
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
            partitioning_info.partitions.append(
                Partition(index=index, part_type=PartTypes.OTHER, part_mount_point="/boot", part_format=True,
                          part_format_type=part_format_type, compute=False))
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
                partitioning_info.partitions.append(
                    Partition(index=index, part_type=PartTypes.EFI, part_mount_point="/boot/efi", part_format=True,
                              part_format_type=FSFormats.VFAT, compute=False))
                index += 1
            else:
                partitioning_info.partitions.append(
                    Partition(index=index, part_type=PartTypes.EFI, part_mount_point="/boot/efi", part_format=False,
                              compute=False))
                index += len(disk.partitions)
        if swap_type == SwapTypes.PARTITION:
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
            partitioning_info.partitions.append(
                Partition(index=index, part_type=PartTypes.SWAP, compute=False))
            index += 1
        if root_block_name:
            # BOOT
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += "+2G\n"  # Last sector (Accept default: varies)
            partitioning_info.partitions.append(
                Partition(index=index, part_type=PartTypes.BOOT, part_mount_point="/boot", part_format=True,
                          part_format_type=part_format_type, compute=False))
            index += 1
        if want_home:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += f'+{root_size}\n'  # Last sector (Accept default: varies)
            partitioning_info.partitions.append(
                Partition(index=index, part_type=PartTypes.ROOT, part_mount_point="/", part_format=True,
                          part_format_type=part_format_type, compute=False))
            index += 1
            # HOME
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            partitioning_info.partitions.append(
                Partition(index=index, part_type=PartTypes.HOME, part_mount_point="/home", part_format=True,
                          part_format_type=part_format_type, compute=False))
            index += 1
        else:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            partitioning_info.partitions.append(
                Partition(index=index, part_type=PartTypes.ROOT, part_mount_point="/", part_format=True,
                          part_format_type=part_format_type, compute=False))
            index += 1
        # WRITE
        auto_part_str += "w\n"

        for partition in partitioning_info.partitions:
            if partition.part_type == PartTypes.ROOT and root_block_name is not None:
                partition.encrypted = True
                partition.block_name = root_block_name
            if partition.part_type == PartTypes.HOME and home_block_name is not None:
                partition.encrypted = True
                partition.block_name = home_block_name

        print_step(_("Summary of choices :"))
        for partition in partitioning_info.partitions:
            print_sub_step(partition.summary())
        if "SWAP" not in [part.part_type for part in partitioning_info.partitions] and swap_size:
            print_sub_step(_("Swapfile size : %s") % swap_size)
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
        if not user_answer:
            want_to_change = prompt_bool(_("Do you want to change the partitioning mode ? (y/N) : "), default=False)
            if want_to_change:
                return None
            partitioning_info.partitions.clear()
        else:
            execute(f'echo -e "{auto_part_str}" | fdisk "{target_disk}" &>/dev/null')

            for partition in partitioning_info.partitions:
                partition.build_partition_name(target_disk)
                partition.compute()

                if partition.part_type == PartTypes.ROOT:
                    partitioning_info.root_partition = partition

                if partition not in partitioning_info.partitions:
                    partitioning_info.partitions.append(partition)

    return partitioning_info
