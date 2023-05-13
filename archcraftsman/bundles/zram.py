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
The zram bundle module
"""
import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.i18n
import archcraftsman.options

_ = archcraftsman.i18n.translate


class Zram(archcraftsman.bundles.bundle.Bundle):
    """
    The ZRAM class.
    """

    def __init__(self):
        super().__init__(archcraftsman.options.Bundles.ZRAM)

    def packages(self) -> list[str]:
        return ["zram-generator"]

    def print_resume(self):
        archcraftsman.base.print_sub_step(_("Install and enable ZRAM."))

    def configure(self):
        content = ["[zram0]\n", "zram-size = ram / 2\n"]
        try:
            with open(
                "/mnt/etc/systemd/zram-generator.conf", "w", encoding="UTF-8"
            ) as zram_config_file:
                zram_config_file.writelines(content)
        except FileNotFoundError as exception:
            archcraftsman.base.log(f"Exception: {exception}")
