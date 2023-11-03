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
The grml zsh bundle module
"""

import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.i18n
import archcraftsman.info
import archcraftsman.options

_ = archcraftsman.i18n.translate


class GrmlZsh(archcraftsman.bundles.bundle.Bundle):
    """
    Grml ZSH config class.
    """

    def __init__(self):
        super().__init__(archcraftsman.options.Bundles.GRML)

    def packages(self) -> list[str]:
        return ["zsh", "zsh-completions", "grml-zsh-config"]

    def prompt(self) -> str:
        return _("Install ZSH with GRML configuration ?")

    def help(self) -> str:
        return _(
            "If yes, the script will install the ZSH shell with GRML "
            "configuration. GRML is a ZSH pre-configuration used by Archlinux's "
            "live environment."
        )

    def print_resume(self):
        archcraftsman.base.print_sub_step(_("Install ZSH with GRML configuration."))

    def configure(self):
        archcraftsman.base.execute("chsh --shell /bin/zsh", chroot=True)
        if archcraftsman.info.ai.system_info.user_name:
            archcraftsman.base.execute(
                f"chsh --shell /bin/zsh {archcraftsman.info.ai.system_info.user_name}",
                chroot=True,
            )
