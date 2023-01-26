"""
The system setup module
"""
import re

from src.bundles.bundle import Bundle
from src.bundles.copyacm import CopyACM
from src.bundles.cups import Cups
from src.bundles.grmlzsh import GrmlZsh
from src.bundles.grub import Grub
from src.bundles.mainfilesystems import get_main_file_systems, MainFileSystems
from src.bundles.mainfonts import get_main_fonts, MainFonts
from src.bundles.microcodes import Microcodes
from src.bundles.nvidia import NvidiaDriver
from src.bundles.pipewire import PipeWire
from src.bundles.terminus import TerminusFont
from src.bundles.utils import prompt_bundle
from src.bundles.zram import Zram
from src.i18n import I18n
from src.options import Kernels, Desktops, Bundles, BootLoaders
from src.utils import print_error, print_step, print_sub_step, prompt_ln, prompt_bool, \
    ask_password, execute

_ = I18n().gettext


def setup_system(detected_timezone) -> {}:
    """
    The method to get system configurations from the user.
    :param detected_timezone:
    :return:
    """
    system_info = {}
    user_answer = False
    while not user_answer:
        print_step(_("System configuration : "))
        system_info["hostname"] = prompt_ln(_("What will be your hostname (archlinux) : "), default="archlinux")
        system_info["bundles"] = []

        system_info["kernel"] = prompt_bundle(_("Choose your kernel (%s) : "), _("Kernel '%s' is not supported."),
                                              Kernels, _("Supported kernels : "), Kernels.CURRENT)

        if prompt_bool(_("Install proprietary Nvidia driver ? (y/N) : "), default=False):
            system_info["bundles"].append(NvidiaDriver(Bundles.NVIDIA))

        if prompt_bool(_("Install terminus console font ? (y/N) : "), default=False):
            system_info["bundles"].append(TerminusFont(Bundles.TERMINUS))

        desktop = prompt_bundle(_("Install a desktop environment ? (%s) : "),
                                _("Desktop environment '%s' is not supported."), Desktops,
                                _("Supported desktop environments : "), Desktops.NONE)
        if desktop is not None:
            system_info["bundles"].append(desktop)

        if prompt_bool(_("Install Cups ? (y/N) : "), default=False):
            system_info["bundles"].append(Cups(Bundles.CUPS))

        if prompt_bool(_("Install ZSH with GRML configuration ? (y/N/?) : "), default=False,
                       help_msg=_(
                           "If yes, the script will install the ZSH shell with GRML "
                           "configuration. GRML is a ZSH pre-configuration used by Archlinux's "
                           "live environment.")):
            system_info["bundles"].append(GrmlZsh(Bundles.GRML))

        if prompt_bool(_("Install a set of main fonts ? (y/N/?) : "), default=False,
                       help_msg=_("If yes, the following packages will be installed :\n%s") % " ".join(
                           get_main_fonts())):
            system_info["bundles"].append(MainFonts(Bundles.MAIN_FONTS))

        if prompt_bool(_("Install main file systems support ? (y/N/?) : "),
                       default=False, help_msg=_(
                    "If yes, the following packages will be installed :\n%s") % " ".join(get_main_file_systems())):
            system_info["bundles"].append(MainFileSystems(Bundles.MAIN_FILE_SYSTEMS))

        if prompt_bool(_("Install and enable ZRAM ? (y/N/?) : "), default=False, help_msg=_(
                "ZRAM is a process to compress datas directly in the RAM instead of moving them in a swap. "
                "Enabled ZRAM will allow you to compress up to half of your RAM before having to swap. "
                "This method is more efficient than the swap and do not use your disk but is more CPU demanding. "
                "ZRAM is fully compatible with a swap, it just has a higher priority.")):
            system_info["bundles"].append(Zram(Bundles.ZRAM))

        if prompt_bool(_("Install PipeWire ? (y/N/?) : "),
                       default=False, help_msg=_(
                    "If yes, the PipeWire multimedia framework will be installed to manage audio and video capture.")):
            system_info["bundles"].append(PipeWire(Bundles.PIPEWIRE))

        if prompt_bool(_("Copy ArchCraftsman to the new system ? (y/N) : "), default=False):
            system_info["bundles"].append(CopyACM(Bundles.COPY_ACM))

        default_timezone_file = f'/usr/share/zoneinfo/{detected_timezone}'
        system_info["timezone"] = prompt_ln(_("Your timezone (%s) : ") % default_timezone_file,
                                            default=default_timezone_file)
        user_name_pattern = re.compile("^[a-z][-a-z\\d_]*$")
        user_name_ok = False
        while not user_name_ok:
            system_info["user_name"] = prompt_ln(_("Would you like to add a user? (type username, leave blank if "
                                                   "none) : "))
            if system_info["user_name"] and system_info["user_name"] != "" and not user_name_pattern.match(
                    system_info["user_name"]):
                print_error(_("Invalid user name."))
                continue
            user_name_ok = True
        system_info["user_full_name"] = ""
        if system_info["user_name"] != "":
            system_info["user_full_name"] = prompt_ln(
                _("What is the %s's full name (type the entire full name, leave blank if none) : ") % system_info[
                    "user_name"])

        pkgs_select_ok = False
        while not pkgs_select_ok:
            system_info["more_pkgs"] = set()
            more_pkgs_str = prompt_ln(
                _("Install more packages ? (type extra packages full names, example : 'htop neofetch', leave blank if "
                  "none) : "))
            pkgs_select_ok = True
            if more_pkgs_str != "":
                for pkg in more_pkgs_str.split():
                    if execute(f'pacman -Si {pkg} &>/dev/null').returncode != 0:
                        pkgs_select_ok = False
                        print_error(_("Package %s doesn't exist.") % pkg)
                        break
                    system_info["more_pkgs"].add(pkg)

        print_sub_step(_("%s password configuration : ") % "root")
        system_info["root_password"] = ask_password(_("Enter the %s password : ") % "root")
        if system_info["user_name"] != "":
            print_sub_step(_("%s password configuration : ") % system_info["user_name"])
            system_info["user_password"] = ask_password(_("Enter the %s password : ") % system_info["user_name"])

        system_info["bootloader"] = Grub(BootLoaders.GRUB)
        system_info["microcodes"] = Microcodes()

        print_step(_("Summary of choices :"))
        print_sub_step(_("Your hostname : %s") % system_info["hostname"])
        system_info["microcodes"].print_resume()
        if system_info["kernel"]:
            system_info["kernel"].print_resume()
        for bundle in system_info["bundles"]:
            if bundle is not None and isinstance(bundle, Bundle):
                bundle.print_resume()
        print_sub_step(_("Your timezone : %s") % system_info["timezone"])
        if system_info["user_name"] != "":
            print_sub_step(_("Additional user name : %s") % system_info["user_name"])
            if system_info["user_full_name"] != "":
                print_sub_step(_("User's full name : %s") % system_info["user_full_name"])
        if system_info["more_pkgs"]:
            print_sub_step(_("More packages to install : %s") % " ".join(system_info["more_pkgs"]))
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
    return system_info
