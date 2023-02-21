"""
The grub bundle module
"""
import re

from src.bundles.bundle import Bundle
from src.options import FSFormats
from src.partitioninginfo import PartitioningInfo
from src.utils import is_bios, execute, stdout


class Grub(Bundle):
    """
    The Grub Bootloader class.
    """

    def packages(self, system_info) -> list[str]:
        return ["grub"]

    def configure(self, system_info: dict, pre_launch_info: dict, partitioning_info: PartitioningInfo):
        if is_bios():
            execute(f'arch-chroot /mnt bash -c "grub-install --target=i386-pc {partitioning_info.main_disk}"')
        else:
            execute(
                'arch-chroot /mnt bash -c "grub-install --target=x86_64-efi --efi-directory=/boot/efi '
                '--bootloader-id=\'Arch Linux\'"')
        execute('sed -i "/^GRUB_CMDLINE_LINUX=.*/a GRUB_DISABLE_OS_PROBER=false" /mnt/etc/default/grub')

        if True in [part.encrypted for part in partitioning_info.partitions]:
            hooks = stdout(
                execute("grep -e '^HOOKS' /mnt/etc/mkinitcpio.conf", check=False, force=True,
                        capture_output=True)).strip()
            pattern = re.compile(r"^HOOKS=\((.+)\)")
            hooks_match = pattern.search(hooks)
            if hooks_match:
                extracted_hooks = hooks_match.group(1).split(" ")
                extracted_hooks.insert(extracted_hooks.index("filesystems"), "encrypt")
            else:
                extracted_hooks = ["encrypt"]
            processed_hooks = f"HOOKS=({' '.join(extracted_hooks)})"
            execute(f'sed -i \'s|{hooks}|{processed_hooks}|g\' /mnt/etc/mkinitcpio.conf')
            execute('arch-chroot /mnt bash -c "mkinitcpio -P"')

        if partitioning_info.root_partition.encrypted:
            partitioning_info.root_partition.compute()
            grub_cmdline = stdout(
                execute("grep -e '^GRUB_CMDLINE_LINUX_DEFAULT' /mnt/etc/default/grub", check=False, force=True,
                        capture_output=True)).strip()
            pattern = re.compile(r'^GRUB_CMDLINE_LINUX_DEFAULT="(.+)"')
            grub_cmdline_match = pattern.search(grub_cmdline)
            if grub_cmdline_match:
                extracted_grub_cmdline = grub_cmdline_match.group(1).split(" ")
            else:
                extracted_grub_cmdline = []
            for partition in [part for part in partitioning_info.partitions if part.encrypted]:
                extracted_grub_cmdline.append(f"cryptdevice=UUID={partition.uuid}:{partition.block_name}")
            extracted_grub_cmdline.append(f"root={partitioning_info.root_partition.real_path()}")
            processed_grub_cmdline = f"GRUB_CMDLINE_LINUX_DEFAULT=\"{' '.join(extracted_grub_cmdline)}\""
            execute(f'sed -i \'s|{grub_cmdline}|{processed_grub_cmdline}|g\' /mnt/etc/default/grub')

        if partitioning_info.root_partition.part_format_type == FSFormats.EXT4:
            execute('sed -i "s|GRUB_DEFAULT=.*|GRUB_DEFAULT=saved|g" /mnt/etc/default/grub')
            execute('sed -i "/^GRUB_DEFAULT=.*/a GRUB_SAVEDEFAULT=true" /mnt/etc/default/grub')
        execute('arch-chroot /mnt bash -c "grub-mkconfig -o /boot/grub/grub.cfg"')
