"""
The bundles related utility methods and tools module
"""
from src.bundles.budgie import Budgie
from src.bundles.bundle import Bundle
from src.bundles.cinnamon import Cinnamon
from src.bundles.cups import Cups
from src.bundles.cutefish import Cutefish
from src.bundles.deepin import Deepin
from src.bundles.enlightenment import Enlightenment
from src.bundles.gnome import Gnome
from src.bundles.grmlzsh import GrmlZsh
from src.bundles.grub import Grub
from src.bundles.i3 import I3
from src.bundles.linux import LinuxCurrent, LinuxLts, LinuxZen, LinuxHardened
from src.bundles.lxqt import Lxqt
from src.bundles.mainfilesystems import MainFileSystems
from src.bundles.mainfonts import MainFonts
from src.bundles.mate import Mate
from src.bundles.microcodes import Microcodes
from src.bundles.nvidia import NvidiaDriver
from src.bundles.pipewire import PipeWire
from src.bundles.plasma import Plasma
from src.bundles.sway import Sway
from src.bundles.terminus import TerminusFont
from src.bundles.xfce import Xfce
from src.bundles.zram import Zram
from src.options import Kernels, BootLoaders, Desktops, Bundles
from src.options import OptionEnum
from src.utils import prompt_option


def process_bundle(name: OptionEnum) -> Bundle or None:
    """
    Process a bundle name into a Bundle object.
    :param name:
    :return:
    """
    bundle = None
    match name:
        case Kernels.CURRENT:
            bundle = LinuxCurrent(name)
        case Kernels.LTS:
            bundle = LinuxLts(name)
        case Kernels.ZEN:
            bundle = LinuxZen(name)
        case Kernels.HARDENED:
            bundle = LinuxHardened(name)
        case BootLoaders.GRUB:
            bundle = Grub(name)
        case Desktops.GNOME:
            bundle = Gnome(name)
        case Desktops.PLASMA:
            bundle = Plasma(name)
        case Desktops.XFCE:
            bundle = Xfce(name)
        case Desktops.BUDGIE:
            bundle = Budgie(name)
        case Desktops.CINNAMON:
            bundle = Cinnamon(name)
        case Desktops.CUTEFISH:
            bundle = Cutefish(name)
        case Desktops.DEEPIN:
            bundle = Deepin(name)
        case Desktops.LXQT:
            bundle = Lxqt(name)
        case Desktops.MATE:
            bundle = Mate(name)
        case Desktops.ENLIGHTENMENT:
            bundle = Enlightenment(name)
        case Desktops.I3:
            bundle = I3(name)
        case Desktops.SWAY:
            bundle = Sway(name)
        case Bundles.CUPS:
            bundle = Cups(name)
        case Bundles.GRML:
            bundle = GrmlZsh(name)
        case Bundles.MAIN_FILE_SYSTEMS:
            bundle = MainFileSystems(name)
        case Bundles.MAIN_FONTS:
            bundle = MainFonts(name)
        case Bundles.MICROCODES:
            bundle = Microcodes()
        case Bundles.NVIDIA:
            bundle = NvidiaDriver(name)
        case Bundles.PIPEWIRE:
            bundle = PipeWire(name)
        case Bundles.TERMINUS:
            bundle = TerminusFont(name)
        case Bundles.ZRAM:
            bundle = Zram(name)
    return bundle


def prompt_bundle(message: str, error_msg: str, options: type(OptionEnum), supported_msg: str or None,
                  default: OptionEnum or None, *ignores: OptionEnum, new_line_prompt: bool = True) -> Bundle or None:
    """
    A method to prompt for a bundle.
    :param new_line_prompt:
    :param supported_msg:
    :param message:
    :param error_msg:
    :param options:
    :param default:
    :return:
    """
    option = prompt_option(message, error_msg, options, supported_msg, default, *ignores,
                           new_line_prompt=new_line_prompt)
    if not option:
        return None
    bundle = process_bundle(option)
    if bundle:
        bundle.prompt_extra()
    return bundle
