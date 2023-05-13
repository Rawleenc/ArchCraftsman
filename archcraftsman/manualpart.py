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
The manual partitioning system module
"""
import archcraftsman.base
import archcraftsman.disk
import archcraftsman.i18n
import archcraftsman.info
import archcraftsman.options
import archcraftsman.partition
import archcraftsman.utils

_ = archcraftsman.i18n.translate


def manual_partitioning(change_disks: bool = True) -> bool:
    """
    The method to proceed to the manual partitioning.
    """
    user_answer = False
    partitioned_disks = []
    while not user_answer:
        archcraftsman.base.print_step(_("Manual partitioning :"))
        archcraftsman.base.print_sub_step(
            _("Partitioned drives so far : %s") % " ".join(partitioned_disks)
        )
        archcraftsman.base.execute("fdisk -l", force=True, sudo=True)
        target_disk = archcraftsman.utils.ask_drive()
        if target_disk not in partitioned_disks:
            partitioned_disks.append(target_disk)
        if change_disks:
            archcraftsman.base.execute(f'cfdisk "{target_disk}"')
        archcraftsman.base.print_step(_("Manual partitioning :"))
        archcraftsman.base.print_sub_step(
            _("Partitioned drives so far : %s") % " ".join(partitioned_disks)
        )
        archcraftsman.base.execute("fdisk -l", force=True, sudo=True)
        other_drive = archcraftsman.utils.prompt_bool(
            _("Do you want to partition an other drive ?"), default=False
        )
        if other_drive:
            continue
        for disk_path in partitioned_disks:
            archcraftsman.base.log(f"Detected disk: {disk_path}")
            disk = archcraftsman.disk.Disk(disk_path)
            partitions = [partition.path for partition in disk.partitions]
            archcraftsman.base.log(f"Partitions: {partitions}")
            for partition in partitions:
                archcraftsman.base.log(f"Partition : {partition}")
                archcraftsman.info.ai.partitioning_info.partitions.append(
                    archcraftsman.partition.Partition(path=partition)
                )
        archcraftsman.base.print_step(
            _("Detected target drive partitions : %s")
            % " ".join(
                [
                    part.path
                    for part in archcraftsman.info.ai.partitioning_info.partitions
                    if part.path
                ]
            )
        )
        for partition in archcraftsman.info.ai.partitioning_info.partitions:
            archcraftsman.base.print_step(_("Partition :"), clear=False)
            archcraftsman.base.print_sub_step(str(partition))
            if archcraftsman.base.is_bios():
                partition_type = archcraftsman.utils.prompt_option(
                    _("What is the role of this partition ? (%s) : "),
                    _("Partition type '%s' is not supported."),
                    archcraftsman.options.PartTypes,
                    _("Supported partition types : "),
                    archcraftsman.options.PartTypes.OTHER,
                    archcraftsman.options.PartTypes.EFI,
                )
            else:
                partition_type = archcraftsman.utils.prompt_option(
                    _("What is the role of this partition ? (%s) : "),
                    _("Partition type '%s' is not supported."),
                    archcraftsman.options.PartTypes,
                    _("Supported partition types : "),
                    archcraftsman.options.PartTypes.OTHER,
                )
            if (
                not archcraftsman.base.is_bios()
                and partition_type == archcraftsman.options.PartTypes.EFI
            ):
                partition.part_type = archcraftsman.options.PartTypes.EFI
                partition.part_mount_point = "/boot/efi"
            elif partition_type == archcraftsman.options.PartTypes.ROOT:
                partition.part_type = archcraftsman.options.PartTypes.ROOT
                partition.part_mount_point = "/"
                archcraftsman.info.ai.partitioning_info.main_disk = (
                    f"/dev/{partition.disk_name()}"
                )
            elif partition_type == archcraftsman.options.PartTypes.BOOT:
                partition.part_type = archcraftsman.options.PartTypes.BOOT
                partition.part_mount_point = "/boot"
            elif partition_type == archcraftsman.options.PartTypes.HOME:
                partition.part_type = archcraftsman.options.PartTypes.HOME
                partition.part_mount_point = "/home"
            elif partition_type == archcraftsman.options.PartTypes.SWAP:
                partition.part_type = archcraftsman.options.PartTypes.SWAP
            elif partition_type == archcraftsman.options.PartTypes.NOT_USED:
                continue
            elif partition_type == archcraftsman.options.PartTypes.OTHER:
                partition.part_type = archcraftsman.options.PartTypes.OTHER
                partition.part_mount_point = archcraftsman.base.prompt(
                    _("What is the mounting point of this partition ? : ")
                )
            partition.ask_for_format()
            partition.ask_for_encryption()

        if (
            not archcraftsman.base.is_bios()
            and archcraftsman.options.PartTypes.EFI
            not in [
                part.part_type
                for part in archcraftsman.info.ai.partitioning_info.partitions
            ]
        ):
            archcraftsman.base.print_error(
                _("The EFI partition is required for system installation.")
            )
            archcraftsman.info.ai.partitioning_info.partitions.clear()
            partitioned_disks.clear()
            continue
        if archcraftsman.options.PartTypes.ROOT not in [
            part.part_type
            for part in archcraftsman.info.ai.partitioning_info.partitions
        ]:
            archcraftsman.base.print_error(
                _("The Root partition is required for system installation.")
            )
            archcraftsman.info.ai.partitioning_info.partitions.clear()
            partitioned_disks.clear()
            continue
        if True in [
            part.encrypted and part.part_type == archcraftsman.options.PartTypes.ROOT
            for part in archcraftsman.info.ai.partitioning_info.partitions
        ] and archcraftsman.options.PartTypes.BOOT not in [
            part.part_type
            for part in archcraftsman.info.ai.partitioning_info.partitions
        ]:
            archcraftsman.base.print_error(
                _("The Boot partition is required for system installation.")
            )
            archcraftsman.info.ai.partitioning_info.partitions.clear()
            partitioned_disks.clear()
            continue
        if archcraftsman.options.PartTypes.SWAP not in [
            part.part_type
            for part in archcraftsman.info.ai.partitioning_info.partitions
        ]:
            archcraftsman.info.ai.partitioning_info.swapfile_size = (
                archcraftsman.disk.Disk(
                    archcraftsman.info.ai.partitioning_info.main_disk
                ).ask_swapfile_size()
            )

        archcraftsman.base.print_step(_("Summary of choices :"))
        for partition in archcraftsman.info.ai.partitioning_info.partitions:
            archcraftsman.base.print_sub_step(partition.summary())
        if (
            archcraftsman.options.PartTypes.SWAP
            not in [
                part.part_type
                for part in archcraftsman.info.ai.partitioning_info.partitions
            ]
            and archcraftsman.info.ai.partitioning_info.swapfile_size
        ):
            archcraftsman.base.print_sub_step(
                _("Swapfile size : %s")
                % archcraftsman.info.ai.partitioning_info.swapfile_size
            )
        user_answer = archcraftsman.utils.prompt_bool(
            _("Is the information correct ?"), default=False
        )
        if not user_answer:
            want_to_change = archcraftsman.utils.prompt_bool(
                _("Do you want to change the partitioning mode ?"), default=False
            )
            if want_to_change:
                return False
            archcraftsman.info.ai.partitioning_info.partitions.clear()
            partitioned_disks.clear()
    return True
