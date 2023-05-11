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
The all available options module.
"""
from enum import Enum, auto


class OptionEnum(str, Enum):
    """
    The Enum base method for options.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list
    ) -> str:
        return name.lower().replace("_", "")

    def __str__(self) -> str:
        return self.value


class Languages(OptionEnum):
    """
    All available languages.
    """

    ENGLISH = auto()
    FRENCH = auto()


class Commands(OptionEnum):
    """
    All available commands.
    """

    KERNEL = auto()
    DESKTOP = auto()
    BUNDLE = auto()
    SHELL_BUNDLE = auto()
    HELP = auto()
    EXIT = auto()


class SubCommands(OptionEnum):
    """
    All available sub-commands.
    """

    INSTALL = auto()
    UNINSTALL = auto()
    CANCEL = auto()


class Kernels(OptionEnum):
    """
    All kernel options.
    """

    CURRENT = auto()
    LTS = auto()
    ZEN = auto()
    HARDENED = auto()


class Desktops(OptionEnum):
    """
    All desktop environment options.
    """

    GNOME = auto()
    PLASMA = auto()
    XFCE = auto()
    BUDGIE = auto()
    CINNAMON = auto()
    CUTEFISH = auto()
    DEEPIN = auto()
    LXQT = auto()
    MATE = auto()
    ENLIGHTENMENT = auto()
    I3 = auto()
    SWAY = auto()
    NONE = auto()


class Network(OptionEnum):
    """
    All network options.
    """

    NETWORK_MANAGER = auto()
    IWD = auto()
    SYSTEMD = auto()
    NONE = auto()


class BootLoaders(OptionEnum):
    """
    All bootloader options.
    """

    GRUB = auto()


class Bundles(OptionEnum):
    """
    All other options.
    """

    GRML = auto()
    MICROCODES = auto()
    NVIDIA = auto()
    TERMINUS = auto()
    ZRAM = auto()
    COPY_ACM = auto()


class ShellBundles(OptionEnum):
    """
    All shell options.
    """

    YAY = auto()
    GENERATE_CONFIG = auto()


class FSFormats(OptionEnum):
    """
    All file system format options.
    """

    VFAT = auto()
    EXT4 = auto()
    BTRFS = auto()


class SwapTypes(OptionEnum):
    """
    All sway type options.
    """

    PARTITION = auto()
    FILE = auto()
    NONE = auto()


class PartTypes(OptionEnum):
    """
    All partition type options.
    """

    EFI = auto()
    ROOT = auto()
    BOOT = auto()
    HOME = auto()
    SWAP = auto()
    NOT_USED = auto()
    OTHER = auto()


class BundleTypes(OptionEnum):
    """
    All bundle type options.
    """

    BOOTLOADER = auto()
    DESKTOP = auto()
    KERNEL = auto()
    MICRO_CODES = auto()
    NETWORK = auto()
    OTHER = auto()


def get_btype_by_name(name: str) -> BundleTypes:
    """
    Get the bundle type by name.
    """
    if name == Bundles.MICROCODES.value:
        return BundleTypes.MICRO_CODES
    if name in [option.value for option in BootLoaders]:
        return BundleTypes.BOOTLOADER
    if name in [option.value for option in Desktops]:
        return BundleTypes.DESKTOP
    if name in [option.value for option in Kernels]:
        return BundleTypes.KERNEL
    if name in [option.value for option in Network]:
        return BundleTypes.NETWORK
    return BundleTypes.OTHER
