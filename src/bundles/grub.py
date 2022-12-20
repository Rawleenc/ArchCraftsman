import os

from src.bundles.bundle import Bundle
from src.utils import is_bios


class Grub(Bundle):
    """
    The Grub Bootloader class.
    """

    def packages(self, system_info) -> [str]:
        return ["grub"]

    def configure(self, system_info: dict, pre_launch_info: dict, partitioning_info: dict):
        if is_bios():
            os.system(f'arch-chroot /mnt bash -c "grub-install --target=i386-pc {partitioning_info["main_disk"]}"')
        else:
            os.system(
                'arch-chroot /mnt bash -c "grub-install --target=x86_64-efi --efi-directory=/boot/efi '
                '--bootloader-id=\'Arch Linux\'"')
        os.system('sed -i "/^GRUB_CMDLINE_LINUX=.*/a GRUB_DISABLE_OS_PROBER=false" /mnt/etc/default/grub')
        if partitioning_info["part_format_type"][partitioning_info["root_partition"]] in {"ext4"}:
            os.system('sed -i "s|GRUB_DEFAULT=.*|GRUB_DEFAULT=saved|g" /mnt/etc/default/grub')
            os.system('sed -i "/^GRUB_DEFAULT=.*/a GRUB_SAVEDEFAULT=true" /mnt/etc/default/grub')
        os.system('arch-chroot /mnt bash -c "grub-mkconfig -o /boot/grub/grub.cfg"')
