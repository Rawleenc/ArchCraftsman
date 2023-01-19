"""
The automatic partitioning system module
"""
import os

from src.disk import Disk
from src.i18n import I18n
from src.utils import ask_format_type, is_bios, from_iec, to_iec, \
    build_partition_name, print_error, print_step, print_sub_step, prompt, prompt_bool

_ = I18n().gettext


def auto_partitioning() -> {}:
    """
    The method to proceed to the automatic partitioning.
    :return:
    """
    partitioning_info_by_index = {"indexes": set(), "part_type": {}, "part_mount_point": {}, "part_format": {},
                                  "part_format_type": {}}
    partitioning_info = {"partitions": set(), "part_type": {}, "part_mount_point": {}, "part_format": {},
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
            partitioning_info_by_index["part_type"][index] = "OTHER"
            partitioning_info_by_index["part_mount_point"][index] = "/boot"
            partitioning_info_by_index["part_format"][index] = True
            partitioning_info_by_index["part_format_type"][index] = part_format_type
            partitioning_info_by_index["indexes"].add(index)
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
                partitioning_info_by_index["part_format"][index] = True
                partitioning_info_by_index["part_format_type"][index] = "vfat"
                partitioning_info_by_index["part_type"][index] = "EFI"
                partitioning_info_by_index["part_mount_point"][index] = "/boot/efi"
                partitioning_info_by_index["indexes"].add(index)
                index += 1
            else:
                partitioning_info_by_index["part_format"][efi_partition.index] = False
                partitioning_info_by_index["part_type"][efi_partition.index] = "EFI"
                partitioning_info_by_index["part_mount_point"][efi_partition.index] = "/boot/efi"
                partitioning_info_by_index["indexes"].add(efi_partition.index)
                index += len(disk.partitions)
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
            partitioning_info_by_index["part_type"][index] = "SWAP"
            partitioning_info_by_index["indexes"].add(index)
            index += 1
        if want_home:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += f'+{root_size}\n'  # Last sector (Accept default: varies)
            partitioning_info_by_index["part_type"][index] = "ROOT"
            partitioning_info_by_index["part_mount_point"][index] = "/"
            partitioning_info_by_index["part_format_type"][index] = part_format_type
            partitioning_info_by_index["indexes"].add(index)
            index += 1
            # HOME
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            partitioning_info_by_index["part_type"][index] = "HOME"
            partitioning_info_by_index["part_mount_point"][index] = "/home"
            partitioning_info_by_index["part_format"][index] = True
            partitioning_info_by_index["part_format_type"][index] = part_format_type
            partitioning_info_by_index["indexes"].add(index)
            index += 1
        else:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            partitioning_info_by_index["part_type"][index] = "ROOT"
            partitioning_info_by_index["part_mount_point"][index] = "/"
            partitioning_info_by_index["part_format_type"][index] = part_format_type
            partitioning_info_by_index["indexes"].add(index)
            index += 1
        # WRITE
        auto_part_str += "w\n"

        print_step(_("Summary of choices :"), clear=False)
        for index in partitioning_info_by_index["indexes"]:
            if partitioning_info_by_index["part_format"].get(index):
                formatting = _("yes")
            else:
                formatting = _("no")
            if partitioning_info_by_index["part_type"].get(index) == "EFI":
                print_sub_step(_("EFI partition : %s (mounting point : %s, format %s, format type %s)")
                               % (index + 1, partitioning_info_by_index["part_mount_point"].get(index), formatting,
                                  partitioning_info_by_index["part_format_type"].get(index)))
            if partitioning_info_by_index["part_type"].get(index) == "ROOT":
                print_sub_step(_("ROOT partition : %s (mounting point : %s, format type %s)")
                               % (index + 1, partitioning_info_by_index["part_mount_point"].get(index),
                                  partitioning_info_by_index["part_format_type"].get(index)))
            if partitioning_info_by_index["part_type"].get(index) == "HOME":
                print_sub_step(_("Home partition : %s (mounting point : %s, format %s, format type %s)")
                               % (index + 1, partitioning_info_by_index["part_mount_point"].get(index), formatting,
                                  partitioning_info_by_index["part_format_type"].get(index)))
            if partitioning_info_by_index["part_type"].get(index) == "SWAP":
                print_sub_step(_("Swap partition : %s") % index + 1)
            if partitioning_info_by_index["part_type"].get(index) == "OTHER":
                print_sub_step(_("Other partition : %s (mounting point : %s, format %s, format type %s)")
                               % (index + 1, partitioning_info_by_index["part_mount_point"].get(index), formatting,
                                  partitioning_info_by_index["part_format_type"].get(index)))
        if "SWAP" not in partitioning_info_by_index["part_type"].values() and swap_size:
            print_sub_step(_("Swapfile size : %s") % swap_size)
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
        if not user_answer:
            want_to_change = prompt_bool(_("Do you want to change the partitioning mode ? (y/N) : "), default=False)
            if want_to_change:
                return None
            partitioning_info_by_index["indexes"].clear()
        else:
            os.system(f'echo -e "{auto_part_str}" | fdisk "{target_disk}" &>/dev/null')

            for index in partitioning_info_by_index["indexes"]:
                partition = build_partition_name(target_disk, index)

                partitioning_info["part_type"][partition] = partitioning_info_by_index["part_type"].get(index)
                partitioning_info["part_mount_point"][partition] = partitioning_info_by_index["part_mount_point"].get(
                    index)
                partitioning_info["part_format_type"][partition] = partitioning_info_by_index["part_format_type"].get(
                    index)
                partitioning_info["part_format"][partition] = partitioning_info_by_index["part_format"].get(index)

                if partitioning_info_by_index["part_type"].get(index) == "ROOT":
                    partitioning_info["root_partition"] = partition

                partitioning_info["partitions"].add(partition)

    return partitioning_info
