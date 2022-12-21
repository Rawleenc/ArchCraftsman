"""
The zram bundle module
"""
from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.utils import print_sub_step

_ = I18n().gettext


class Zram(Bundle):
    """
    The ZRAM class.
    """

    def packages(self, system_info: {}) -> [str]:
        return ["zram-generator"]

    def print_resume(self):
        print_sub_step(_("Install and enable ZRAM."))

    def configure(self, system_info, pre_launch_info, partitioning_info):
        content = [
            "[zram0]\n",
            "zram-size = ram / 2\n"
        ]
        with open("/mnt/etc/systemd/zram-generator.conf", "w", encoding="UTF-8") as zram_config_file:
            zram_config_file.writelines(content)
