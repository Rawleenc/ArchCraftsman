"""
The all available options module.
"""
from enum import Enum, auto

from src.i18n import I18n

_ = I18n().gettext


class OptionEnum(str, Enum):
    """
    The Enum base method for options.
    """

    @staticmethod
    def _generate_next_value_(name: str, start: int, count: int, last_values: list) -> str:
        return name.lower().replace("_", "")

    def __str__(self):
        return _(self.name.lower().replace('_', ' ').capitalize())


class Kernel(OptionEnum):
    """
    All kernel options.
    """
    CURRENT = auto()
    LTS = auto()
    ZEN = auto()
    HARDENED = auto()


class DesktopEnv(OptionEnum):
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


class BootLoader(OptionEnum):
    """
    All bootloader options.
    """
    GRUB = auto()


class Other(OptionEnum):
    """
    All other options.
    """
    CUPS = auto()
    GRML = auto()
    MAIN_FILE_SYSTEMS = auto()
    MAIN_FONTS = auto()
    MICROCODES = auto()
    NVIDIA = auto()
    PIPEWIRE = auto()
    TERMINUS = auto()
    ZRAM = auto()


class FSFormat(OptionEnum):
    """
    All file system format options.
    """
    VFAT = auto()
    EXT4 = auto()
    BTRFS = auto()


class Swap(OptionEnum):
    """
    All sway type options.
    """
    PARTITION = auto()
    FILE = auto()
    NONE = auto()


class PartType(OptionEnum):
    """
    All partition type options.
    """
    EFI = auto()
    ROOT = auto()
    HOME = auto()
    SWAP = auto()
    NOT_USED = auto()
    OTHER = auto()
