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
I18n messages translation keys.
"""
import archcraftsman.i18n

_ = archcraftsman.i18n.translate

CUPS_PROMPT = _("Install Cups ?")
CUPS_RESUME = _("Install Cups.")
MAIN_FS_PROMPT = _("Install main file systems support ?")
MAIN_FS_RESUME = _("Install main file systems support.")
PKGS_LIST_HELP = _("If yes, the following packages will be installed :\n{packages}")
MAIN_FONTS_PROMPT = _("Install a set of main fonts ?")
MAIN_FONTS_RESUME = _("Install a set of main fonts.")
PIPEWIRE_PROMPT = _("Install PipeWire ?")
PIPEWIRE_RESUME = _("Install PipeWire.")
PIPEWIRE_HELP = _(
    "If yes, the PipeWire multimedia framework will be installed to manage audio and video capture."
)
MULTILIB_PROMPT = _("Enable Multilib repository ?")
MULTILIB_RESUME = _("Enable Multilib repository.")
