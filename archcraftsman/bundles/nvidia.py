# ArchCraftsman, The careful yet very fast Arch Linux Craftsman.
# Copyright (C) 2023 Rawleenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
The nvidia proprietary driver bundle module
"""
from archcraftsman import info
from archcraftsman.base import print_sub_step
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import _
from archcraftsman.options import Bundles, Kernels


class NvidiaDriver(Bundle):
    """
    The Nvidia driver class.
    """

    def __init__(self):
        super().__init__(Bundles.NVIDIA)

    def packages(self) -> list[str]:
        if (
            info.ai.system_info.kernel()
            and info.ai.system_info.kernel().name == Kernels.LTS
        ):
            return ["nvidia-lts"]
        return ["nvidia"]

    def print_resume(self):
        print_sub_step(_("Install proprietary Nvidia driver."))
