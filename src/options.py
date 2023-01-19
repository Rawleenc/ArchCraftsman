from enum import IntEnum, auto


class OptionEnum(IntEnum):

    def __str__(self):
        return self._name_.lower()

    def title(self):
        return "%s: %s" % (self._value_, self._name_)


class Kernel(OptionEnum):
    CURRENT = auto()
    LTS = auto()
    ZEN = auto()
    HARDENED = auto()


class DesktopEnv(OptionEnum):
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
    GRUB = auto()


class Other(OptionEnum):
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
    EXT4 = auto()
    BTRFS = auto()


class Swap(OptionEnum):
    FILE = auto()
    PARTITION = auto()
    NONE = auto()
