import os
import re

from src.bundles.bundle import Bundle
from src.bundles.i18n import I18n
from src.utils import print_sub_step

_ = I18n().gettext

class Microcodes(Bundle):
    """
    The Microcodes class.
    """

    def __init__(self):
        super().__init__(re.sub('\\s+', '', os.popen('grep </proc/cpuinfo "vendor" | uniq').read()).split(":")[1])

    def packages(self, system_info: {}) -> [str]:
        if self.name == "GenuineIntel":
            return ["intel-ucode"]
        if self.name == "AuthenticAMD":
            return ["amd-ucode"]
        return []

    def microcode_img(self) -> str or None:
        """
        The microcode img file name retrieving method.
        """
        if self.name == "GenuineIntel":
            return "/intel-ucode.img"
        if self.name == "AuthenticAMD":
            return "/amd-ucode.img"
        return None

    def print_resume(self):
        if self.name in {"GenuineIntel", "AuthenticAMD"}:
            print_sub_step(_("Microcodes to install : %s") % self.name)
