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
import enum
import typing


class OptionEnum(str, enum.Enum):
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

    ENGLISH = enum.auto()
    FRENCH = enum.auto()


class Commands(OptionEnum):
    """
    All available commands.
    """

    KERNEL = enum.auto()
    DESKTOP = enum.auto()
    BUNDLE = enum.auto()
    SHELL_BUNDLE = enum.auto()
    HELP = enum.auto()
    EXIT = enum.auto()


class SubCommands(OptionEnum):
    """
    All available sub-commands.
    """

    INSTALL = enum.auto()
    UNINSTALL = enum.auto()
    CANCEL = enum.auto()


class Kernels(OptionEnum):
    """
    All kernel options.
    """

    CURRENT = enum.auto()
    LTS = enum.auto()
    ZEN = enum.auto()
    HARDENED = enum.auto()


class Desktops(OptionEnum):
    """
    All desktop environment options.
    """

    GNOME = enum.auto()
    PLASMA = enum.auto()
    XFCE = enum.auto()
    NONE = enum.auto()


class Network(OptionEnum):
    """
    All network options.
    """

    NETWORK_MANAGER = enum.auto()
    IWD = enum.auto()
    SYSTEMD = enum.auto()
    NONE = enum.auto()


class BootLoaders(OptionEnum):
    """
    All bootloader options.
    """

    GRUB = enum.auto()


class Bundles(OptionEnum):
    """
    All other options.
    """

    GRML = enum.auto()
    MICROCODES = enum.auto()
    NVIDIA = enum.auto()
    TERMINUS = enum.auto()
    ZRAM = enum.auto()
    COPY_ACM = enum.auto()
    ARCHITECT = enum.auto()


class ShellBundles(OptionEnum):
    """
    All shell options.
    """

    YAY = enum.auto()
    GENERATE_CONFIG = enum.auto()


class FSFormats(OptionEnum):
    """
    All file system format options.
    """

    VFAT = enum.auto()
    EXT4 = enum.auto()
    BTRFS = enum.auto()


class SwapTypes(OptionEnum):
    """
    All swap type options.
    """

    PARTITION = enum.auto()
    FILE = enum.auto()
    NONE = enum.auto()


class PartTypes(OptionEnum):
    """
    All partition type options.
    """

    EFI = enum.auto()
    ROOT = enum.auto()
    BOOT = enum.auto()
    HOME = enum.auto()
    SWAP = enum.auto()
    NOT_USED = enum.auto()
    OTHER = enum.auto()


class BundleTypes(OptionEnum):
    """
    All bundle type options.
    """

    BOOTLOADER = enum.auto()
    DESKTOP = enum.auto()
    KERNEL = enum.auto()
    MICRO_CODES = enum.auto()
    NETWORK = enum.auto()
    OTHER = enum.auto()


class PartTypeInformations:
    """
    The partition type informations.
    """

    def __init__(
        self,
        part_type: PartTypes,
        part_mount_point: str,
        supported_formats: list[FSFormats],
    ) -> None:
        self.part_type = part_type
        self.part_mount_point = part_mount_point
        self.supported_formats = supported_formats

    def __str__(self) -> str:
        return f"Type : {self.part_type}, Mount point : {self.part_mount_point}"


def get_type_info(
    part_type: PartTypes = PartTypes.OTHER,
) -> typing.Optional[PartTypeInformations]:
    """
    Get the supported formats for a partition type.
    """
    base_formats = [FSFormats.BTRFS, FSFormats.EXT4]
    return {
        PartTypes.EFI: PartTypeInformations(
            part_type=PartTypes.EFI,
            part_mount_point="/boot/efi",
            supported_formats=[FSFormats.VFAT],
        ),
        PartTypes.ROOT: PartTypeInformations(
            part_type=PartTypes.ROOT,
            part_mount_point="/",
            supported_formats=base_formats,
        ),
        PartTypes.BOOT: PartTypeInformations(
            part_type=PartTypes.BOOT,
            part_mount_point="/boot",
            supported_formats=base_formats + [FSFormats.VFAT],
        ),
        PartTypes.HOME: PartTypeInformations(
            part_type=PartTypes.HOME,
            part_mount_point="/home",
            supported_formats=base_formats,
        ),
    }.get(part_type)


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
