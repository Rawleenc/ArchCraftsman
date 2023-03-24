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
The module of SystemInfo class.
"""

from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import I18n

_ = I18n().gettext


class SystemInfo:
    """
    The class to contain all system information.
    """

    hostname: str
    bundles: list[Bundle]
    kernel: Bundle
    desktop: Bundle
    network: Bundle
    bootloader: Bundle
    micro_codes: Bundle
    timezone: str
    user_name: str
    user_full_name: str
    more_pkgs: set[str]
    root_password: str
    user_password: str
