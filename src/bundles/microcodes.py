"""
The microcodes auto-installation bundle module
"""
import re

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.options import Other
from src.utils import print_sub_step, execute, stdout

_ = I18n().gettext


class Microcodes(Bundle):
    """
    The Microcodes class.
    """

    def __init__(self):
        super().__init__(Other.MICROCODES)
        cpu_info_vendor = stdout(execute('grep </proc/cpuinfo "vendor" | uniq', capture_output=True))
        if cpu_info_vendor:
            self.microcode_name = re.sub('\\s+', '', cpu_info_vendor).split(":")[1]
        else:
            self.microcode_name = None

    def packages(self, system_info: {}) -> [str]:
        if self.microcode_name == "GenuineIntel":
            return ["intel-ucode"]
        if self.microcode_name == "AuthenticAMD":
            return ["amd-ucode"]
        return []

    def microcode_img(self) -> str or None:
        """
        The microcode img file name retrieving method.
        """
        if self.microcode_name == "GenuineIntel":
            return "/intel-ucode.img"
        if self.microcode_name == "AuthenticAMD":
            return "/amd-ucode.img"
        return None

    def print_resume(self):
        if self.microcode_name in {"GenuineIntel", "AuthenticAMD"}:
            print_sub_step(_("Microcodes to install : %s") % self.microcode_name)
