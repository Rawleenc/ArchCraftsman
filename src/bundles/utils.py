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
from src.utils import print_error, print_step, print_sub_step, prompt_ln


def process_bundle(name: str) -> Bundle or None:
    """
    Process a bundle name into a Bundle object.
    :param name:
    :return:
    """
    bundle = None
    match name:
        case "current":
            bundle = LinuxCurrent("current")
        case "lts":
            bundle = LinuxLts("lts")
        case "zen":
            bundle = LinuxZen("zen")
        case "hardened":
            bundle = LinuxHardened("hardened")
        case "grub":
            bundle = Grub("grub")
        case "gnome":
            bundle = Gnome("gnome")
        case "plasma":
            bundle = Plasma("plasma")
        case "xfce":
            bundle = Xfce("xfce")
        case "budgie":
            bundle = Budgie("budgie")
        case "cinnamon":
            bundle = Cinnamon("cinnamon")
        case "cutefish":
            bundle = Cutefish("cutefish")
        case "deepin":
            bundle = Deepin("deepin")
        case "lxqt":
            bundle = Lxqt("lxqt")
        case "mate":
            bundle = Mate("mate")
        case "enlightenment":
            bundle = Enlightenment("enlightenment")
        case "i3":
            bundle = I3("i3")
        case "sway":
            bundle = Sway("sway")
    return bundle


def prompt_bundle(supported_msg: str, message: str, error_msg: str, default_bundle: str,
                  supported_bundles: [str]) -> Bundle or None:
    """
    A method to prompt for a bundle.
    :param supported_msg:
    :param message:
    :param error_msg:
    :param default_bundle:
    :param supported_bundles:
    :return:
    """
    print_step(supported_msg, clear=False)
    print_sub_step(", ".join(supported_bundles))
    print('')
    bundle_ok = False
    bundle = None
    while not bundle_ok:
        bundle_name = prompt_ln(
            message % default_bundle,
            default=default_bundle).lower()
        if bundle_name in supported_bundles:
            bundle_ok = True
            bundle = process_bundle(bundle_name)
        else:
            print_error(error_msg % bundle_name, do_pause=False)
            continue
    if bundle:
        bundle.prompt_extra()
    return bundle
