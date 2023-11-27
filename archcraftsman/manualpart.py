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
    partitioned_disks: list[str] = []
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

            ignored_part_types = []
            if archcraftsman.base.is_bios():
                ignored_part_types.append(archcraftsman.options.PartTypes.EFI)

            partition_type = archcraftsman.utils.prompt_option(
                _("What is the role of this partition ? (%s) : "),
                _("Partition type '%s' is not supported."),
                archcraftsman.options.PartTypes,
                _("Supported partition types : "),
                archcraftsman.options.PartTypes.OTHER,
                *ignored_part_types,
            )

            if (
                not partition_type
                or partition_type == archcraftsman.options.PartTypes.NOT_USED
            ):
                continue

            partition.configure(partition_type)
            partition.ask_for_format()
            partition.ask_for_encryption()

        root_disk_name = (
            archcraftsman.info.ai.partitioning_info.root_partition().disk_name()
        )
        archcraftsman.info.ai.partitioning_info.main_disk = f"/dev/{root_disk_name}"

        if not check_required_partitions(partitioned_disks):
            continue

        ask_swapfile_size()

        archcraftsman.base.print_step(_("Summary of choices :"))
        for partition in archcraftsman.info.ai.partitioning_info.partitions:
            archcraftsman.base.print_sub_step(partition.summary())
        print_swapfile_size()

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


def ask_swapfile_size():
    if archcraftsman.options.PartTypes.SWAP not in [
        part.part_type for part in archcraftsman.info.ai.partitioning_info.partitions
    ] and archcraftsman.options.FSFormats.BTRFS not in [
        part.part_format
        for part in archcraftsman.info.ai.partitioning_info.partitions
        if part.part_type == archcraftsman.options.PartTypes.ROOT
    ]:
        archcraftsman.info.ai.partitioning_info.swapfile_size = archcraftsman.disk.Disk(
            archcraftsman.info.ai.partitioning_info.main_disk
        ).ask_swapfile_size()


def print_swapfile_size():
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


def check_required_partitions(partitioned_disks: list[str]) -> bool:
    if (
        not archcraftsman.base.is_bios()
        and archcraftsman.options.PartTypes.EFI
        not in [
            part.part_type
            for part in archcraftsman.info.ai.partitioning_info.partitions
        ]
        and archcraftsman.options.PartTypes.BOOT
        not in [
            part.part_type
            for part in archcraftsman.info.ai.partitioning_info.partitions
            if part.part_format_type == archcraftsman.options.FSFormats.VFAT
        ]
    ):
        archcraftsman.base.print_error(
            _(
                "An EFI partition or a VFAT formatted Boot partition is required for system installation."
            )
        )
        archcraftsman.info.ai.partitioning_info.partitions.clear()
        partitioned_disks.clear()
        return False

    if archcraftsman.options.PartTypes.ROOT not in [
        part.part_type for part in archcraftsman.info.ai.partitioning_info.partitions
    ]:
        archcraftsman.base.print_error(
            _("The Root partition is required for system installation.")
        )
        archcraftsman.info.ai.partitioning_info.partitions.clear()
        partitioned_disks.clear()
        return False

    if True in [
        part.encrypted and part.part_type == archcraftsman.options.PartTypes.ROOT
        for part in archcraftsman.info.ai.partitioning_info.partitions
    ] and archcraftsman.options.PartTypes.BOOT not in [
        part.part_type for part in archcraftsman.info.ai.partitioning_info.partitions
    ]:
        archcraftsman.base.print_error(
            _("The Boot partition is required for system installation.")
        )
        archcraftsman.info.ai.partitioning_info.partitions.clear()
        partitioned_disks.clear()
        return False

    return True
