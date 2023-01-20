"""
The microcodes auto-installation bundle module
"""
import re

from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.options import Other
from src.utils import print_sub_step, execute

_ = I18n().gettext


class Microcodes(Bundle):
    """
    The Microcodes class.
    """

    def __init__(self):
        super().__init__(Other.MICROCODES)
        self.microcode_name = \
            re.sub('\\s+', '', execute('grep </proc/cpuinfo "vendor" | uniq', capture_output=True).stdout).split(":")[1]

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
