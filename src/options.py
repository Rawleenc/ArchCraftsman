"""
The all available options module.
"""
from enum import IntEnum, auto


class OptionEnum(IntEnum):
    """
    The Enum base method for options.
    """

    def __str__(self):
        """
        __str__ override to return the name in lowercase.
        :return:
        """
        return self.name.lower()

    def title(self):
        """
        A method to display the option's human-readable title
        :return:
        """
        return "%s: %s" % (self.value, self.name.lower())


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
    NONE = auto()
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
    MAINFILESYSTEMS = auto()
    MAINFONTS = auto()
    MICROCODES = auto()
    NVIDIA = auto()
    PIPEWIRE = auto()
    TERMINUS = auto()
    ZRAM = auto()


class FSFormat(OptionEnum):
    """
    All file system format options.
    """
    EXT4 = auto()
    BTRFS = auto()


class Swap(OptionEnum):
    """
    All sway type options.
    """
    FILE = auto()
    PARTITION = auto()
    NONE = auto()
