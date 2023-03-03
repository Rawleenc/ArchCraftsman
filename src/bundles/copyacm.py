"""
The copy ArchCraftsman bundle module
"""
from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.partitioninginfo import PartitioningInfo
from src.prelaunchinfo import PreLaunchInfo
from src.systeminfo import SystemInfo
from src.utils import print_sub_step, execute

_ = I18n().gettext


class CopyACM(Bundle):
    """
    The CopyACM class.
    """

    def print_resume(self):
        print_sub_step(_("Copy ArchCraftsman to the new system."))

    def configure(self, system_info: SystemInfo, pre_launch_info: PreLaunchInfo, partitioning_info: PartitioningInfo):
        if system_info.user_name != "":
            path = f'/home/{system_info.user_name}/ArchCraftsman'
            execute(f'mkdir -p /mnt{path}')
            execute(f'cp -r ~/src /mnt{path}')
            execute(f'cp -r ~/locales /mnt{path}')
            execute(f'arch-chroot /mnt bash -c "chown -R {system_info.user_name}:{system_info.user_name} {path}"')
        else:
            path = "/root/ArchCraftsman"
            execute(f'mkdir -p /mnt{path}')
            execute(f'cp -r ~/src /mnt{path}')
            execute(f'cp -r ~/locales /mnt{path}')
