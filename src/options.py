from enum import StrEnum, auto


class Kernel(StrEnum):
    CURRENT = auto()
    LTS = auto()
    ZEN = auto()
    HARDENED = auto()


class DesktopEnv(StrEnum):
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


class BootLoader(StrEnum):
    GRUB = auto()


class Other(StrEnum):
    CUPS = auto()
    GRML = auto()
    MAINFILESYSTEMS = auto()
    MAINFONTS = auto()
    MICROCODES = auto()
    NVIDIA = auto()
    PIPEWIRE = auto()
    TERMINUS = auto()
    ZRAM = auto()


class FSFormat(StrEnum):
    EXT4 = auto()
    BTRFS = auto()


class Swap(StrEnum):
    FILE = auto()
    PARTITION = auto()
    NONE = auto()
