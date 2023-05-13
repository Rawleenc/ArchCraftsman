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

import archcraftsman.bundles.bundle
import archcraftsman.options


class SystemInfo:
    """
    The class to contain all system information.
    """

    def __init__(
        self,
        hostname: str = "archlinux",
        timezone: str = "Etc/UTC",
        user_name: str = "",
        user_full_name: str = "",
        root_password: str = "",
        user_password: str = "",
    ) -> None:
        self.hostname = hostname
        self.bundles: list[archcraftsman.bundles.bundle.Bundle] = []
        self.timezone = timezone
        self.user_name = user_name
        self.user_full_name = user_full_name
        self.more_pkgs: list[str] = []
        self.root_password = root_password
        self.user_password = user_password

    def kernel(self) -> archcraftsman.bundles.bundle.Bundle:
        """
        The kernel bundle retrieving method.
        """
        return next(
            bundle
            for bundle in self.bundles
            if archcraftsman.options.get_btype_by_name(bundle.name)
            == archcraftsman.options.BundleTypes.KERNEL
        )

    def microcode(self) -> archcraftsman.bundles.bundle.Bundle:
        """
        The microcode bundle retrieving method.
        """
        return next(
            bundle
            for bundle in self.bundles
            if archcraftsman.options.get_btype_by_name(bundle.name)
            == archcraftsman.options.BundleTypes.MICRO_CODES
        )

    def bootloader(self) -> archcraftsman.bundles.bundle.Bundle:
        """
        The bootloader bundle retrieving method.
        """
        return next(
            bundle
            for bundle in self.bundles
            if archcraftsman.options.get_btype_by_name(bundle.name)
            == archcraftsman.options.BundleTypes.BOOTLOADER
        )

    def desktop(self) -> archcraftsman.bundles.bundle.Bundle:
        """
        The desktop bundle retrieving method.
        """
        return next(
            bundle
            for bundle in self.bundles
            if archcraftsman.options.get_btype_by_name(bundle.name)
            == archcraftsman.options.BundleTypes.DESKTOP
        )

    def network(self) -> archcraftsman.bundles.bundle.Bundle:
        """
        The network bundle retrieving method.
        """
        return next(
            bundle
            for bundle in self.bundles
            if archcraftsman.options.get_btype_by_name(bundle.name)
            == archcraftsman.options.BundleTypes.NETWORK
        )

    def others(self) -> list[archcraftsman.bundles.bundle.Bundle]:
        """
        The other bundles retrieving method.
        """
        return [
            bundle
            for bundle in self.bundles
            if archcraftsman.options.get_btype_by_name(bundle.name)
            == archcraftsman.options.BundleTypes.OTHER
        ]
