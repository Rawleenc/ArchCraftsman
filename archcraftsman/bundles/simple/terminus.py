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
The terminus console font bundle module
"""

import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.i18n
import archcraftsman.info
import archcraftsman.options

_ = archcraftsman.i18n.translate


class TerminusFont(archcraftsman.bundles.bundle.Bundle):
    """
    The Terminus console font class.
    """

    def __init__(self):
        super().__init__(archcraftsman.options.Bundles.TERMINUS)

    def packages(self) -> list[str]:
        return ["terminus-font"]

    def prompt(self) -> str:
        return _("Install terminus console font ?")

    def print_resume(self):
        archcraftsman.base.print_sub_step(_("Install terminus console font."))

    def configure(self):
        archcraftsman.base.execute(
            f'echo "FONT={archcraftsman.info.ai.pre_launch_info.live_console_font}" >>/mnt/etc/vconsole.conf'
        )
