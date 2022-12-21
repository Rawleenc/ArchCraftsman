import os

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.utils import print_sub_step

_ = I18n().gettext


class TerminusFont(Bundle):
    """
    The Terminus console font class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["terminus-font"]

    def print_resume(self):
        print_sub_step(_("Install terminus console font."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        os.system(f'echo "FONT={pre_launch_info["live_console_font"]}" >>/mnt/etc/vconsole.conf')
