import os
import re

from src.archcraftsman import _
from src.disk import Disk
from src.utils import print_step, print_sub_step, prompt, print_error, prompt_bool, is_bios, ask_format_type, \
    ask_swapfile_size


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
