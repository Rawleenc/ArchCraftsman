"""
The zram bundle module
"""
from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.utils import print_sub_step, execute

_ = I18n().gettext


class CopyACM(Bundle):
    """
    The ZRAM class.
    """

    def print_resume(self):
        print_sub_step(_("Copy ArchCraftsman to the new system."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        if system_info["user_name"] != "":
            execute(f'mkdir -p /mnt/home/{system_info["user_name"]}/ArchCraftsman')
            execute(f'cp -r ~/src /mnt/home/{system_info["user_name"]}/ArchCraftsman')
            execute(f'cp -r ~/locales /mnt/home/{system_info["user_name"]}/ArchCraftsman')
        else:
            execute("mkdir -p /mnt/root/ArchCraftsman")
            execute("cp -r ~/src /mnt/root/ArchCraftsman")
            execute("cp -r ~/locales /mnt/root/ArchCraftsman")
