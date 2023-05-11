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
The grub bundle module
"""
import re

from archcraftsman import info
from archcraftsman.base import execute, is_bios
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.options import BootLoaders, FSFormats, PartTypes


class Grub(Bundle):
    """
    The Grub Bootloader class.
    """

    def __init__(self):
        super().__init__(BootLoaders.GRUB)

    def packages(self) -> list[str]:
        return ["grub"]

    def configure(self):
        if is_bios():
            execute(
                f"grub-install --target=i386-pc {info.ai.partitioning_info.main_disk}",
                chroot=True,
            )
        else:
            execute(
                "grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id='Arch Linux'",
                chroot=True,
            )
        execute(
            'sed -i "/^GRUB_CMDLINE_LINUX=.*/a GRUB_DISABLE_OS_PROBER=false" /mnt/etc/default/grub'
        )

        if info.ai.partitioning_info.root_partition().encrypted:
            hooks = execute(
                "grep -e '^HOOKS' /mnt/etc/mkinitcpio.conf",
                check=False,
                capture_output=True,
            ).output.strip()
            pattern = re.compile(r"^HOOKS=\((.+)\)")
            hooks_match = pattern.search(hooks)
            if hooks_match:
                extracted_hooks = hooks_match.group(1).split(" ")
                extracted_hooks.insert(extracted_hooks.index("filesystems"), "encrypt")
            else:
                extracted_hooks = ["encrypt"]
            processed_hooks = f"HOOKS=({' '.join(extracted_hooks)})"
            execute(f"sed -i 's|{hooks}|{processed_hooks}|g' /mnt/etc/mkinitcpio.conf")
            execute("mkinitcpio -P", chroot=True)

            grub_cmdline = execute(
                "grep -e '^GRUB_CMDLINE_LINUX_DEFAULT' /mnt/etc/default/grub",
                check=False,
                capture_output=True,
            ).output.strip()
            pattern = re.compile(r'^GRUB_CMDLINE_LINUX_DEFAULT="(.+)"')
            grub_cmdline_match = pattern.search(grub_cmdline)
            if grub_cmdline_match:
                extracted_grub_cmdline = grub_cmdline_match.group(1).split(" ")
            else:
                extracted_grub_cmdline = []
            extracted_grub_cmdline.append(
                f"cryptdevice=UUID={info.ai.partitioning_info.root_partition().uuid()}:root"
            )
            processed_grub_cmdline = (
                f"GRUB_CMDLINE_LINUX_DEFAULT=\"{' '.join(extracted_grub_cmdline)}\""
            )
            execute(
                f"sed -i 's|{grub_cmdline}|{processed_grub_cmdline}|g' /mnt/etc/default/grub"
            )

        for partition in [
            part
            for part in info.ai.partitioning_info.partitions
            if part.encrypted and part.part_type != PartTypes.ROOT
        ]:
            execute(
                f'echo "{partition.block_name} UUID={partition.uuid()} none" >> /mnt/etc/crypttab'
            )

        if (
            info.ai.partitioning_info.root_partition().part_format_type
            == FSFormats.EXT4
        ):
            execute(
                'sed -i "s|GRUB_DEFAULT=.*|GRUB_DEFAULT=saved|g" /mnt/etc/default/grub'
            )
            execute(
                'sed -i "/^GRUB_DEFAULT=.*/a GRUB_SAVEDEFAULT=true" /mnt/etc/default/grub'
            )
        execute("grub-mkconfig -o /boot/grub/grub.cfg", chroot=True)
