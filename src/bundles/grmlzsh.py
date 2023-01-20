"""
The grml zsh bundle module
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.utils import print_sub_step, execute

_ = I18n().gettext


class GrmlZsh(Bundle):
    """
    Grml ZSH config class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["zsh", "zsh-completions", "grml-zsh-config"]

    def print_resume(self):
        print_sub_step(_("Install ZSH with GRML configuration."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        execute('arch-chroot /mnt bash -c "chsh --shell /bin/zsh"')
        execute(f'arch-chroot /mnt bash -c "chsh --shell /bin/zsh {system_info["user_name"]}"')
