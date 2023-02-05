"""
The grub bundle module
"""

from src.bundles.bundle import Bundle
from src.options import FSFormats
from src.partitioninginfo import PartitioningInfo
from src.utils import is_bios, execute


class Grub(Bundle):
    """
    The Grub Bootloader class.
    """

    def packages(self, system_info) -> [str]:
        return ["grub"]

    def configure(self, system_info: dict, pre_launch_info: dict, partitioning_info: PartitioningInfo):
        if is_bios():
            execute(f'arch-chroot /mnt bash -c "grub-install --target=i386-pc {partitioning_info.main_disk}"')
        else:
            execute(
                'arch-chroot /mnt bash -c "grub-install --target=x86_64-efi --efi-directory=/boot/efi '
                '--bootloader-id=\'Arch Linux\'"')
        execute('sed -i "/^GRUB_CMDLINE_LINUX=.*/a GRUB_DISABLE_OS_PROBER=false" /mnt/etc/default/grub')
        if partitioning_info.root_partition.part_format_type == FSFormats.EXT4:
            execute('sed -i "s|GRUB_DEFAULT=.*|GRUB_DEFAULT=saved|g" /mnt/etc/default/grub')
            execute('sed -i "/^GRUB_DEFAULT=.*/a GRUB_SAVEDEFAULT=true" /mnt/etc/default/grub')
        execute('arch-chroot /mnt bash -c "grub-mkconfig -o /boot/grub/grub.cfg"')
