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
import archcraftsman.base
import archcraftsman.disk
import archcraftsman.i18n
import archcraftsman.info
import archcraftsman.options
import archcraftsman.partition
import archcraftsman.utils

_ = archcraftsman.i18n.translate


def auto_partitioning() -> bool:
    """
    The method to proceed to the automatic partitioning.
    """
    user_answer = False
    while not user_answer:
        archcraftsman.base.print_step(_("Automatic partitioning :"))
        archcraftsman.base.execute("fdisk -l", force=True, sudo=True)
        target_disk = archcraftsman.utils.ask_drive()
        archcraftsman.info.ai.partitioning_info.main_disk = target_disk
        disk = archcraftsman.disk.Disk(target_disk)
        efi_partition = disk.get_efi_partition()
        if (
            not archcraftsman.base.is_bios()
            and len(disk.partitions) > 0
            and efi_partition.path
            and efi_partition.fs_type() == "vfat"
            and disk.free_space > archcraftsman.utils.from_iec("32G")
        ):
            want_dual_boot = archcraftsman.utils.prompt_bool(
                _("Do you want to install Arch Linux next to other systems ?")
            )
        else:
            want_dual_boot = False

        swap_type = archcraftsman.utils.prompt_option(
            _("What type of Swap do you want ? (%s) : "),
            _("Swap type '%s' is not supported."),
            archcraftsman.options.SwapTypes,
            supported_msg=_("Supported Swap types : "),
            default=archcraftsman.options.SwapTypes.FILE,
        )

        want_home = archcraftsman.utils.prompt_bool(_("Do you want a separated Home ?"))
        part_format_type = archcraftsman.utils.ask_format_type()
        root_block_name = None
        if archcraftsman.utils.prompt_bool(
            _("Do you want to encrypt the %s partition ?") % "Root", default=False
        ):
            root_block_name = "root"
        home_block_name = None
        if want_home:
            if archcraftsman.utils.prompt_bool(
                _("Do you want to encrypt the %s partition ?") % "Home", default=False
            ):
                home_block_name = "home"

        if want_dual_boot:
            root_size = archcraftsman.utils.to_iec(int(disk.free_space / 4))
            swap_size = archcraftsman.utils.to_iec(int(disk.free_space / 32))
        else:
            root_size = archcraftsman.utils.to_iec(int(disk.total / 4))
            swap_size = archcraftsman.utils.to_iec(int(disk.total / 32))
        if swap_type == archcraftsman.options.SwapTypes.NONE:
            swap_size = ""
        archcraftsman.info.ai.partitioning_info.swapfile_size = swap_size
        auto_part_str = ""
        index = 0
        if archcraftsman.base.is_bios():
            # DOS LABEL
            auto_part_str += "o\n"  # Create a new empty DOS partition table
            # BOOT
            auto_part_str += "n\n"  # Add a new partition
            auto_part_str += (
                "p\n"  # archcraftsman.disk.Partition primary (Accept default: primary)
            )
            auto_part_str += (
                " \n"  # archcraftsman.disk.Partition number (Accept default: auto)
            )
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += "+2G\n"  # Last sector (Accept default: varies)
            auto_part_str += "a\n"  # Toggle bootable flag
            archcraftsman.info.ai.partitioning_info.partitions.append(
                archcraftsman.partition.Partition(
                    index=index,
                    part_type=archcraftsman.options.PartTypes.BOOT,
                    part_mount_point="/boot",
                    part_format=True,
                    part_format_type=part_format_type,
                )
            )
            index += 1
        else:
            if not want_dual_boot:
                # GPT LABEL
                auto_part_str += "g\n"  # Create a new empty GPT partition table
                # EFI
                auto_part_str += "n\n"  # Add a new partition
                auto_part_str += (
                    " \n"  # archcraftsman.disk.Partition number (Accept default: auto)
                )
                auto_part_str += " \n"  # First sector (Accept default: 1)
                auto_part_str += "+512M\n"  # Last sector (Accept default: varies)
                auto_part_str += "t\n"  # Change partition type
                auto_part_str += (
                    " \n"  # archcraftsman.disk.Partition number (Accept default: auto)
                )
                auto_part_str += "1\n"  # Type EFI System
                archcraftsman.info.ai.partitioning_info.partitions.append(
                    archcraftsman.partition.Partition(
                        index=index,
                        part_type=archcraftsman.options.PartTypes.EFI,
                        part_mount_point="/boot/efi",
                        part_format=True,
                        part_format_type=archcraftsman.options.FSFormats.VFAT,
                    )
                )
                index += 1
            else:
                archcraftsman.info.ai.partitioning_info.partitions.append(
                    archcraftsman.partition.Partition(
                        index=index,
                        part_type=archcraftsman.options.PartTypes.EFI,
                        part_mount_point="/boot/efi",
                        part_format=False,
                    )
                )
                index += len(disk.partitions)
        if swap_type == archcraftsman.options.SwapTypes.PARTITION:
            # SWAP
            auto_part_str += "n\n"  # Add a new partition
            if archcraftsman.base.is_bios():
                auto_part_str += "p\n"  # archcraftsman.disk.Partition primary (Accept default: primary)
            auto_part_str += (
                " \n"  # archcraftsman.disk.Partition number (Accept default: auto)
            )
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += f"+{swap_size}\n"  # Last sector (Accept default: varies)
            auto_part_str += "t\n"  # Change partition type
            auto_part_str += (
                " \n"  # archcraftsman.disk.Partition number (Accept default: auto)
            )
            if archcraftsman.base.is_bios():
                auto_part_str += "82\n"  # Type Linux Swap
            else:
                auto_part_str += "19\n"  # Type Linux Swap
            archcraftsman.info.ai.partitioning_info.partitions.append(
                archcraftsman.partition.Partition(
                    index=index, part_type=archcraftsman.options.PartTypes.SWAP
                )
            )
            index += 1
        if (
            root_block_name
            or part_format_type
            in (
                archcraftsman.options.FSFormats.BTRFS,
                archcraftsman.options.FSFormats.XFS,
            )
        ) and not any(
            p.part_type == archcraftsman.options.PartTypes.BOOT
            for p in archcraftsman.info.ai.partitioning_info.partitions
        ):
            # BOOT
            auto_part_str += "n\n"  # Add a new partition
            if archcraftsman.base.is_bios():
                auto_part_str += "p\n"  # archcraftsman.disk.Partition primary (Accept default: primary)
            auto_part_str += (
                " \n"  # archcraftsman.disk.Partition number (Accept default: auto)
            )
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += "+2G\n"  # Last sector (Accept default: varies)
            archcraftsman.info.ai.partitioning_info.partitions.append(
                archcraftsman.partition.Partition(
                    index=index,
                    part_type=archcraftsman.options.PartTypes.BOOT,
                    part_mount_point="/boot",
                    part_format=True,
                    part_format_type=archcraftsman.options.FSFormats.EXT4,
                )
            )
            index += 1
        if want_home:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if archcraftsman.base.is_bios():
                auto_part_str += "p\n"  # archcraftsman.disk.Partition primary (Accept default: primary)
            auto_part_str += (
                " \n"  # archcraftsman.disk.Partition number (Accept default: auto)
            )
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += f"+{root_size}\n"  # Last sector (Accept default: varies)
            archcraftsman.info.ai.partitioning_info.partitions.append(
                archcraftsman.partition.Partition(
                    index=index,
                    part_type=archcraftsman.options.PartTypes.ROOT,
                    part_mount_point="/",
                    part_format=True,
                    part_format_type=part_format_type,
                )
            )
            index += 1
            # HOME
            auto_part_str += "n\n"  # Add a new partition
            if archcraftsman.base.is_bios():
                auto_part_str += "p\n"  # archcraftsman.disk.Partition primary (Accept default: primary)
            auto_part_str += (
                " \n"  # archcraftsman.disk.Partition number (Accept default: auto)
            )
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            archcraftsman.info.ai.partitioning_info.partitions.append(
                archcraftsman.partition.Partition(
                    index=index,
                    part_type=archcraftsman.options.PartTypes.HOME,
                    part_mount_point="/home",
                    part_format=True,
                    part_format_type=part_format_type,
                )
            )
            index += 1
        else:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if archcraftsman.base.is_bios():
                auto_part_str += "p\n"  # archcraftsman.disk.Partition primary (Accept default: primary)
            auto_part_str += (
                " \n"  # archcraftsman.disk.Partition number (Accept default: auto)
            )
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            archcraftsman.info.ai.partitioning_info.partitions.append(
                archcraftsman.partition.Partition(
                    index=index,
                    part_type=archcraftsman.options.PartTypes.ROOT,
                    part_mount_point="/",
                    part_format=True,
                    part_format_type=part_format_type,
                )
            )
            index += 1
        # WRITE
        auto_part_str += "w\n"

        for partition in archcraftsman.info.ai.partitioning_info.partitions:
            if (
                partition.part_type == archcraftsman.options.PartTypes.ROOT
                and root_block_name is not None
            ):
                partition.encrypted = True
                partition.block_name = root_block_name
            if (
                partition.part_type == archcraftsman.options.PartTypes.HOME
                and home_block_name is not None
            ):
                partition.encrypted = True
                partition.block_name = home_block_name

        archcraftsman.base.print_step(_("Summary of choices :"))
        for partition in archcraftsman.info.ai.partitioning_info.partitions:
            archcraftsman.base.print_sub_step(partition.summary())
        if swap_type == archcraftsman.options.SwapTypes.FILE and swap_size is not None:
            archcraftsman.base.print_sub_step(_("Swapfile size : %s") % swap_size)
        user_answer = archcraftsman.utils.prompt_bool(
            _("Is the information correct ?"), default=False
        )
        if not user_answer:
            want_to_change = archcraftsman.utils.prompt_bool(
                _("Do you want to change the partitioning mode ?"), default=False
            )
            archcraftsman.info.ai.partitioning_info.partitions.clear()
            if want_to_change:
                return False
        else:
            archcraftsman.base.execute(
                f'echo -e "{auto_part_str}" | fdisk "{target_disk}" &>/dev/null'
            )

            for partition in archcraftsman.info.ai.partitioning_info.partitions:
                partition.build_partition_name(target_disk)

                if partition not in archcraftsman.info.ai.partitioning_info.partitions:
                    archcraftsman.info.ai.partitioning_info.partitions.append(partition)

    return True
