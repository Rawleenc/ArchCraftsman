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
from archcraftsman.options import BundleTypes

_ = I18n().gettext


class SystemInfo:
    """
    The class to contain all system information.
    """

    hostname: str = "archlinux"
    bundles: list[Bundle] = []
    timezone: str = "Etc/UTC"
    user_name: str = ""
    user_full_name: str = ""
    more_pkgs: list[str] = []
    root_password: str = ""
    user_password: str = ""

    def kernel(self) -> Bundle:
        """
        The kernel bundle retrieving method.
        """
        return [
            bundle
            for bundle in self.bundles
            if bundle.bundle_type == BundleTypes.KERNEL
        ][0]

    def microcode(self) -> Bundle:
        """
        The microcode bundle retrieving method.
        """
        return next(
            bundle
            for bundle in self.bundles
            if bundle.bundle_type == BundleTypes.MICRO_CODES
        )

    def bootloader(self) -> Bundle:
        """
        The bootloader bundle retrieving method.
        """
        return next(
            bundle
            for bundle in self.bundles
            if bundle.bundle_type == BundleTypes.BOOTLOADER
        )

    def desktop(self) -> Bundle:
        """
        The desktop bundle retrieving method.
        """
        return next(
            bundle
            for bundle in self.bundles
            if bundle.bundle_type == BundleTypes.DESKTOP
        )

    def network(self) -> Bundle:
        """
        The network bundle retrieving method.
        """
        return next(
            bundle
            for bundle in self.bundles
            if bundle.bundle_type == BundleTypes.NETWORK
        )

    def others(self) -> list[Bundle]:
        """
        The other bundles retrieving method.
        """
        return [
            bundle for bundle in self.bundles if bundle.bundle_type == BundleTypes.OTHER
        ]
