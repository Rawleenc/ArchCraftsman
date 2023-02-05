"""
The manual partitioning system module
"""
import os
import re

from src.disk import Disk
from src.i18n import I18n
from src.options import PartTypes, FSFormats
from src.partition import Partition
from src.partitioninginfo import PartitioningInfo
from src.utils import is_bios, ask_format_type, \
    print_error, print_step, print_sub_step, prompt, prompt_bool, prompt_option, execute, stdout, log

_ = I18n().gettext


def manual_partitioning() -> PartitioningInfo or None:
    """
    The method to proceed to the manual partitioning.
    :return:
    """
    partitioning_info = PartitioningInfo()
    user_answer = False
    partitioned_disks = []
    while not user_answer:
        print_step(_("Manual partitioning :"))
        print_sub_step(_("Partitioned drives so far : %s") % " ".join(partitioned_disks))
        execute('fdisk -l', force=True)
        target_disk = prompt(
            _("Which drive do you want to partition ? (type the entire name, for example '/dev/sda') : "))
        if not os.path.exists(target_disk):
            print_error(_("The chosen target drive doesn't exist."))
            continue
        if target_disk not in partitioned_disks:
            partitioned_disks.append(target_disk)
        execute(f'cfdisk "{target_disk}"')
        print_step(_("Manual partitioning :"))
        print_sub_step(_("Partitioned drives so far : %s") % " ".join(partitioned_disks))
        execute('fdisk -l', force=True)
        other_drive = prompt_bool(_("Do you want to partition an other drive ? (y/N) : "), default=False)
        if other_drive:
            continue
        for disk in partitioned_disks:
            log(f"Detected disk: {disk}")
            detected_partitions = stdout(execute(
                f'lsblk -nl "{disk}" -o PATH,PARTTYPENAME | grep -iE "linux|efi|swap" | awk \'{{print $1}}\'',
                capture_output=True, force=True))
            log(f"Partitions: {detected_partitions.splitlines()}")
            for partition in detected_partitions.splitlines():
                log(f"Partition : {partition}")
                partitioning_info.partitions.append(Partition(path=partition))
        print_step(
            _("Detected target drive partitions : %s") % " ".join([part.path for part in partitioning_info.partitions]))
        for partition in partitioning_info.partitions:
            print_step(_("Partition :"), clear=False)
            print_sub_step(partition)
            if is_bios():
                partition_type = prompt_option(_("What is the role of this partition ? (%s) : "),
                                               _("Partition type '%s' is not supported."), PartTypes,
                                               _("Supported partition types : "), PartTypes.OTHER,
                                               PartTypes.EFI)
            else:
                partition_type = prompt_option(_("What is the role of this partition ? (%s) : "),
                                               _("Partition type '%s' is not supported."), PartTypes,
                                               _("Supported partition types : "), PartTypes.OTHER)
            if not is_bios() and partition_type == PartTypes.EFI:
                partition.part_type = PartTypes.EFI
                partition.part_mount_point = "/boot/efi"
                partition.part_format = prompt_bool(_("Format the partition ? (Y/n) : "))
                if partition.part_format:
                    partition.part_format_type = FSFormats.VFAT
            elif partition_type == PartTypes.ROOT:
                partition.part_type = PartTypes.ROOT
                partition.part_mount_point = "/"
                partition.part_format = True
                partition.part_format_type = ask_format_type()
                partitioning_info.root_partition = partition
                main_disk_label = re.sub('\\s+', '',
                                         stdout(execute(f'lsblk -ndo PKNAME {partition.path}', capture_output=True,
                                                        force=True)))
                partitioning_info.main_disk = f'/dev/{main_disk_label}'
            elif partition_type == PartTypes.BOOT:
                partition.part_type = PartTypes.BOOT
                partition.part_mount_point = "/boot"
                partition.part_format = prompt_bool(_("Format the partition ? (Y/n) : "))
                if partition.part_format:
                    partition.part_format_type = ask_format_type()
            elif partition_type == PartTypes.HOME:
                partition.part_type = PartTypes.HOME
                partition.part_mount_point = "/home"
                partition.part_format = prompt_bool(_("Format the partition ? (Y/n) : "))
                if partition.part_format:
                    partition.part_format_type = ask_format_type()
            elif partition_type == PartTypes.SWAP:
                partition.part_type = PartTypes.SWAP
            elif partition_type == PartTypes.NOT_USED:
                continue
            elif partition_type == PartTypes.OTHER:
                partition.part_type = PartTypes.OTHER
                partition.part_mount_point = prompt(
                    _("What is the mounting point of this partition ? : "))
                partition.part_format = prompt_bool(
                    _("Format the %s partition ? (Y/n) : ") % partition)
                if partition.part_format:
                    partition.part_format_type = ask_format_type()
        if not is_bios() and PartTypes.EFI not in [part.part_type for part in partitioning_info.partitions]:
            print_error(_("The EFI partition is required for system installation."))
            partitioning_info.partitions.clear()
            partitioned_disks.clear()
            continue
        if PartTypes.ROOT not in [part.part_type for part in partitioning_info.partitions]:
            print_error(_("The Root partition is required for system installation."))
            partitioning_info.partitions.clear()
            partitioned_disks.clear()
            continue
        if True in [part.encrypted for part in partitioning_info.partitions] and PartTypes.BOOT not in \
                [part.part_type for part in partitioning_info.partitions]:
            print_error(_("The Boot partition is required for system installation."))
            partitioning_info.partitions.clear()
            partitioned_disks.clear()
            continue
        if PartTypes.SWAP not in [part.part_type for part in partitioning_info.partitions]:
            partitioning_info.swapfile_size = Disk(partitioning_info.main_disk).ask_swapfile_size()
        print_step(_("Summary of choices :"))
        for partition in partitioning_info.partitions:
            print_sub_step(partition.summary())
        if PartTypes.SWAP not in [part.part_type for part in
                                  partitioning_info.partitions] and partitioning_info.swapfile_size:
            print_sub_step(_("Swapfile size : %s") % partitioning_info.swapfile_size)
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
        if not user_answer:
            want_to_change = prompt_bool(_("Do you want to change the partitioning mode ? (y/N) : "), default=False)
            if want_to_change:
                return None
            partitioning_info.partitions.clear()
            partitioned_disks.clear()
    return partitioning_info
