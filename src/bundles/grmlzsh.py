"""
The grml zsh bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.partitioninginfo import PartitioningInfo
from src.prelaunchinfo import PreLaunchInfo
from src.systeminfo import SystemInfo
from src.utils import print_sub_step, execute

_ = I18n().gettext


class GrmlZsh(Bundle):
    """
    Grml ZSH config class.
    """

    def packages(self, system_info: SystemInfo) -> list[str]:
        return ["zsh", "zsh-completions", "grml-zsh-config"]

    def print_resume(self):
        print_sub_step(_("Install ZSH with GRML configuration."))

    def configure(
        self,
        system_info: SystemInfo,
        pre_launch_info: PreLaunchInfo,
        partitioning_info: PartitioningInfo,
    ):
        execute('arch-chroot /mnt bash -c "chsh --shell /bin/zsh"')
        execute(
            f'arch-chroot /mnt bash -c "chsh --shell /bin/zsh {system_info.user_name}"'
        )
