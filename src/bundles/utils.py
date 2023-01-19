"""
The bundles related utility methods and tools module
"""
from src.bundles.budgie import Budgie
from src.bundles.bundle import Bundle
from src.bundles.cinnamon import Cinnamon
from src.bundles.cutefish import Cutefish
from src.bundles.deepin import Deepin
from src.bundles.enlightenment import Enlightenment
from src.bundles.gnome import Gnome
from src.bundles.grub import Grub
from src.bundles.i3 import I3
from src.bundles.linux import LinuxCurrent, LinuxLts, LinuxZen, LinuxHardened
from src.bundles.lxqt import Lxqt
from src.bundles.mate import Mate
from src.bundles.plasma import Plasma
from src.bundles.sway import Sway
from src.bundles.xfce import Xfce
from src.options import Kernel, BootLoader, DesktopEnv
from src.utils import prompt_option
from src.options import OptionEnum


def process_bundle(name: OptionEnum) -> Bundle or None:
    """
    Process a bundle name into a Bundle object.
    :param name:
    :return:
    """
    bundle = None
    match name:
        case Kernel.CURRENT:
            bundle = LinuxCurrent(name)
        case Kernel.LTS:
            bundle = LinuxLts(name)
        case Kernel.ZEN:
            bundle = LinuxZen(name)
        case Kernel.HARDENED:
            bundle = LinuxHardened(name)
        case BootLoader.GRUB:
            bundle = Grub(name)
        case DesktopEnv.GNOME:
            bundle = Gnome(name)
        case DesktopEnv.PLASMA:
            bundle = Plasma(name)
        case DesktopEnv.XFCE:
            bundle = Xfce(name)
        case DesktopEnv.BUDGIE:
            bundle = Budgie(name)
        case DesktopEnv.CINNAMON:
            bundle = Cinnamon(name)
        case DesktopEnv.CUTEFISH:
            bundle = Cutefish(name)
        case DesktopEnv.DEEPIN:
            bundle = Deepin(name)
        case DesktopEnv.LXQT:
            bundle = Lxqt(name)
        case DesktopEnv.MATE:
            bundle = Mate(name)
        case DesktopEnv.ENLIGHTENMENT:
            bundle = Enlightenment(name)
        case DesktopEnv.I3:
            bundle = I3(name)
        case DesktopEnv.SWAY:
            bundle = Sway(name)
    return bundle


def prompt_bundle(supported_msg: str, message: str, error_msg: str, options: type(OptionEnum)) -> Bundle or None:
    """
    A method to prompt for a bundle.
    :param supported_msg:
    :param message:
    :param error_msg:
    :param options:
    :return:
    """
    option = prompt_option(supported_msg, message, error_msg, options)
    if not option:
        return None
    bundle = process_bundle(option)
    if bundle:
        bundle.prompt_extra()
    return bundle
