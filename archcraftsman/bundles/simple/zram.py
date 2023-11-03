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

    def prompt(self) -> str:
        return _("Install and enable ZRAM ?")

    def help(self) -> str:
        return _(
            "ZRAM is a process to compress datas directly in the RAM instead of moving them in a swap. "
            "Enabled ZRAM will allow you to compress up to half of your RAM before having to swap. "
            "This method is more efficient than the swap and do not use your disk but is more CPU demanding. "
            "ZRAM is fully compatible with a swap, it just has a higher priority."
        )

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
