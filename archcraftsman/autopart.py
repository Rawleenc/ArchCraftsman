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
The automatic partitioning system module
"""
from archcraftsman.disk import Disk
from archcraftsman.i18n import I18n
from archcraftsman.options import FSFormats, PartTypes, SwapTypes
from archcraftsman.partition import Partition
from archcraftsman.partitioninginfo import PartitioningInfo
from archcraftsman.utils import (
    ask_drive,
    ask_format_type,
    execute,
    from_iec,
    is_bios,
    print_step,
    print_sub_step,
    prompt_bool,
    prompt_option,
    to_iec,
)

_ = I18n().gettext


def auto_partitioning() -> tuple[bool, PartitioningInfo]:
    """
    The method to proceed to the automatic partitioning.
    """
    partitioning_info = PartitioningInfo()
    user_answer = False
    while not user_answer:
        print_step(_("Automatic partitioning :"))
        execute("fdisk -l", force=True)
        target_disk = ask_drive(
            _(
                "On which drive should Archlinux be installed ? (type the entire name, for example '/dev/sda') : "
            ),
            _("The target drive '%s' doesn't exist."),
            _("Detected drives :"),
        )
        partitioning_info.main_disk = target_disk
        disk = Disk(target_disk)
        efi_partition = disk.get_efi_partition()
        if (
            not is_bios()
            and len(disk.partitions) > 0
            and efi_partition.path
            and efi_partition.fs_type == "vfat"
            and disk.free_space > from_iec("32G")
        ):
            want_dual_boot = prompt_bool(
                _("Do you want to install Arch Linux next to other systems ?")
            )
        else:
            want_dual_boot = False

        swap_type = prompt_option(
            _("What type of Swap do you want ? (%s) : "),
            _("Swap type '%s' is not supported."),
            SwapTypes,
            supported_msg=_("Supported Swap types : "),
            default=SwapTypes.FILE,
        )

        want_home = prompt_bool(_("Do you want a separated Home ?"))
        part_format_type = ask_format_type()
        root_block_name = None
        if prompt_bool(
            _("Do you want to encrypt the %s partition ?") % "Root", default=False
        ):
            root_block_name = "root"
        home_block_name = None
        if want_home:
            if prompt_bool(
                _("Do you want to encrypt the %s partition ?") % "Home", default=False
            ):
                home_block_name = "home"

        if want_dual_boot:
            root_size = to_iec(int(disk.free_space / 4))
            swap_size = to_iec(int(disk.free_space / 32))
        else:
            root_size = to_iec(int(disk.total / 4))
            swap_size = to_iec(int(disk.total / 32))
        if swap_type == SwapTypes.NONE:
            swap_size = None
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
                Partition(
                    index=index,
                    part_type=PartTypes.OTHER,
                    part_mount_point="/boot",
                    part_format=True,
                    part_format_type=part_format_type,
                    compute=False,
                )
            )
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
                    Partition(
                        index=index,
                        part_type=PartTypes.EFI,
                        part_mount_point="/boot/efi",
                        part_format=True,
                        part_format_type=FSFormats.VFAT,
                        compute=False,
                    )
                )
                index += 1
            else:
                partitioning_info.partitions.append(
                    Partition(
                        index=index,
                        part_type=PartTypes.EFI,
                        part_mount_point="/boot/efi",
                        part_format=False,
                        compute=False,
                    )
                )
                index += len(disk.partitions)
        if swap_type == SwapTypes.PARTITION:
            # SWAP
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += f"+{swap_size}\n"  # Last sector (Accept default: varies)
            auto_part_str += "t\n"  # Change partition type
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            if is_bios():
                auto_part_str += "82\n"  # Type Linux Swap
            else:
                auto_part_str += "19\n"  # Type Linux Swap
            partitioning_info.partitions.append(
                Partition(index=index, part_type=PartTypes.SWAP, compute=False)
            )
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
                Partition(
                    index=index,
                    part_type=PartTypes.BOOT,
                    part_mount_point="/boot",
                    part_format=True,
                    part_format_type=part_format_type,
                    compute=False,
                )
            )
            index += 1
        if want_home:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += f"+{root_size}\n"  # Last sector (Accept default: varies)
            partitioning_info.partitions.append(
                Partition(
                    index=index,
                    part_type=PartTypes.ROOT,
                    part_mount_point="/",
                    part_format=True,
                    part_format_type=part_format_type,
                    compute=False,
                )
            )
            index += 1
            # HOME
            auto_part_str += "n\n"  # Add a new partition
            if is_bios():
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            partitioning_info.partitions.append(
                Partition(
                    index=index,
                    part_type=PartTypes.HOME,
                    part_mount_point="/home",
                    part_format=True,
                    part_format_type=part_format_type,
                    compute=False,
                )
            )
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
                Partition(
                    index=index,
                    part_type=PartTypes.ROOT,
                    part_mount_point="/",
                    part_format=True,
                    part_format_type=part_format_type,
                    compute=False,
                )
            )
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
        if swap_type == SwapTypes.FILE and swap_size is not None:
            print_sub_step(_("Swapfile size : %s") % swap_size)
        user_answer = prompt_bool(_("Is the information correct ?"), default=False)
        if not user_answer:
            want_to_change = prompt_bool(
                _("Do you want to change the partitioning mode ?"), default=False
            )
            if want_to_change:
                return False, partitioning_info
            partitioning_info.partitions.clear()
        else:
            execute(f'echo -e "{auto_part_str}" | fdisk "{target_disk}" &>/dev/null')

            for partition in partitioning_info.partitions:
                partition.build_partition_name(target_disk)

                if partition.part_type == PartTypes.ROOT:
                    partitioning_info.root_partition = partition

                if partition not in partitioning_info.partitions:
                    partitioning_info.partitions.append(partition)

    return True, partitioning_info
