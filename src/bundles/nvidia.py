"""
The nvidia proprietary driver bundle module
"""
from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.options import Kernels
from src.systeminfo import SystemInfo
from src.utils import print_sub_step

_ = I18n().gettext


class NvidiaDriver(Bundle):
    """
    The Nvidia driver class.
    """

    def packages(self, system_info: SystemInfo) -> list[str]:
        if system_info.kernel.name == Kernels.LTS:
            return ["nvidia-lts"]
        return ["nvidia"]

    def print_resume(self):
        print_sub_step(_("Install proprietary Nvidia driver."))
