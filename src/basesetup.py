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
from src.options import Kernels, Desktops, Bundles, BootLoaders, Network
from src.prelaunchinfo import PreLaunchInfo
from src.systeminfo import SystemInfo
from src.utils import print_error, print_step, print_sub_step, prompt_ln, prompt_bool, \
    ask_password, execute, is_bios

_ = I18n().gettext


def initial_setup(detected_language: str, detected_timezone: str) -> PreLaunchInfo:
    """
    The method to get environment configurations from the user.
    :param detected_language:
    :param detected_timezone:
    :return:
    """
    pre_launch_info = PreLaunchInfo()
    user_answer = False
    while not user_answer:
        print_step(_("Welcome to ArchCraftsman !"))
        if is_bios():
            print_error(
                _("BIOS detected ! The script will act accordingly. Don't forget to select a DOS label type before "
                  "partitioning."))

        print_step(_("Environment configuration : "), clear=False)

        supported_global_languages = ["FR", "EN"]
        if detected_language == "fr-FR":
            default_language = "FR"
        else:
            default_language = "EN"

        print_step(_("Supported languages : "), clear=False)
        print_sub_step(", ".join(supported_global_languages))
        print('')
        global_language_ok = False
        pre_launch_info.global_language = ""
        pre_launch_info.keymap = ""
        while not global_language_ok:
            pre_launch_info.global_language = prompt_ln(
                _("Choose your installation's language (%s) : ") % default_language,
                default=default_language).upper()
            if pre_launch_info.global_language in supported_global_languages:
                global_language_ok = True
            else:
                print_error(_("Global language '%s' is not supported.") % pre_launch_info.global_language,
                            do_pause=False)
                continue

        if detected_language == "fr-FR":
            default_keymap = "fr-latin9"
        else:
            default_keymap = "de-latin1"

        keymap_ok = False
        while not keymap_ok:
            pre_launch_info.keymap = prompt_ln(_("Type your installation's keymap (%s) : ") % default_keymap,
                                               default=default_keymap)
            if execute(f'localectl list-keymaps | grep "^{pre_launch_info.keymap}$" &>/dev/null').returncode == 0:
                keymap_ok = True
            else:
                print_error(_("Keymap %s doesn't exist.") % pre_launch_info.keymap)
                continue

        print_step(_("Summary of choices :"), clear=False)
        print_sub_step(_("Your installation's language : %s") % pre_launch_info.global_language)
        print_sub_step(_("Your installation's keymap : %s") % pre_launch_info.keymap)
        user_answer = prompt_bool(_("Is the information correct ?"), default=False)
    pre_launch_info.detected_timezone = detected_timezone
    pre_launch_info.setup_locale()
    return pre_launch_info


def setup_system(detected_timezone) -> SystemInfo:
    """
    The method to get system configurations from the user.
    :param detected_timezone:
    :return:
    """
    system_setup = SystemInfo()
    user_answer = False
    while not user_answer:
        print_step(_("System configuration : "))
        system_setup.hostname = prompt_ln(_("What will be your hostname (archlinux) : "), default="archlinux")
        system_setup.bundles = []

        system_setup.kernel = prompt_bundle(_("Choose your kernel (%s) : "), _("Kernel '%s' is not supported."),
                                            Kernels, _("Supported kernels : "), Kernels.CURRENT)

        system_setup.desktop = prompt_bundle(_("Install a desktop environment ? (%s) : "),
                                             _("Desktop environment '%s' is not supported."), Desktops,
                                             _("Supported desktop environments : "), Desktops.NONE)

        system_setup.network = prompt_bundle(_("Choose your network stack (%s) : "),
                                             _("Network stack '%s' is not supported."),
                                             Network, _("Supported network stacks : "), Network.NETWORK_MANAGER)

        if prompt_bool(_("Install proprietary Nvidia driver ?"), default=False):
            system_setup.bundles.append(NvidiaDriver(Bundles.NVIDIA))

        if prompt_bool(_("Install terminus console font ?"), default=False):
            system_setup.bundles.append(TerminusFont(Bundles.TERMINUS))

        if prompt_bool(_("Install Cups ?"), default=False):
            system_setup.bundles.append(Cups(Bundles.CUPS))

        if prompt_bool(_("Install ZSH with GRML configuration ?"), default=False,
                       help_msg=_(
                           "If yes, the script will install the ZSH shell with GRML "
                           "configuration. GRML is a ZSH pre-configuration used by Archlinux's "
                           "live environment.")):
            system_setup.bundles.append(GrmlZsh(Bundles.GRML))

        if prompt_bool(_("Install a set of main fonts ?"), default=False,
                       help_msg=_("If yes, the following packages will be installed :\n%s") % " ".join(
                           get_main_fonts())):
            system_setup.bundles.append(MainFonts(Bundles.MAIN_FONTS))

        if prompt_bool(_("Install main file systems support ?"),
                       default=False, help_msg=_(
                    "If yes, the following packages will be installed :\n%s") % " ".join(get_main_file_systems())):
            system_setup.bundles.append(MainFileSystems(Bundles.MAIN_FILE_SYSTEMS))

        if prompt_bool(_("Install and enable ZRAM ?"), default=False, help_msg=_(
                "ZRAM is a process to compress datas directly in the RAM instead of moving them in a swap. "
                "Enabled ZRAM will allow you to compress up to half of your RAM before having to swap. "
                "This method is more efficient than the swap and do not use your disk but is more CPU demanding. "
                "ZRAM is fully compatible with a swap, it just has a higher priority.")):
            system_setup.bundles.append(Zram(Bundles.ZRAM))

        if prompt_bool(_("Install PipeWire ?"),
                       default=False, help_msg=_(
                    "If yes, the PipeWire multimedia framework will be installed "
                    "to manage audio and video capture.")):
            system_setup.bundles.append(PipeWire(Bundles.PIPEWIRE))

        if prompt_bool(_("Copy ArchCraftsman to the new system ?"), default=False):
            system_setup.bundles.append(CopyACM(Bundles.COPY_ACM))

        default_timezone_file = f'/usr/share/zoneinfo/{detected_timezone}'
        system_setup.timezone = prompt_ln(_("Your timezone (%s) : ") % default_timezone_file,
                                          default=default_timezone_file)
        user_name_pattern = re.compile("^[a-z][-a-z\\d_]*$")
        user_name_ok = False
        while not user_name_ok:
            system_setup.user_name = prompt_ln(_("Would you like to add a user? (type username, leave blank if "
                                                 "none) : "))
            if system_setup.user_name and not user_name_pattern.match(
                    system_setup.user_name):
                print_error(_("Invalid user name."))
                continue
            user_name_ok = True
        system_setup.user_full_name = ""
        if system_setup.user_name:
            system_setup.user_full_name = prompt_ln(
                _("What is the %s's full name (type the entire full name, leave blank if none) : ") %
                system_setup.user_name)

        pkgs_select_ok = False
        while not pkgs_select_ok:
            system_setup.more_pkgs = set()
            more_pkgs_str = prompt_ln(
                _("Install more packages ? (type extra packages full names, example : 'htop neofetch', "
                  "leave blank if none) : "))
            pkgs_select_ok = True
            if more_pkgs_str:
                for pkg in more_pkgs_str.split():
                    if execute(f'pacman -Si {pkg} &>/dev/null', check=False).returncode != 0:
                        pkgs_select_ok = False
                        print_error(_("Package %s doesn't exist.") % pkg)
                        break
                    system_setup.more_pkgs.add(pkg)

        print_sub_step(_("%s password configuration : ") % "root")
        system_setup.root_password = ask_password(_("Enter the %s password : ") % "root")
        if system_setup.user_name:
            print_sub_step(_("%s password configuration : ") % system_setup.user_name)
            system_setup.user_password = ask_password(_("Enter the %s password : ") % system_setup.user_name)

        system_setup.bootloader = Grub(BootLoaders.GRUB)
        system_setup.micro_codes = Microcodes()

        print_step(_("Summary of choices :"))
        print_sub_step(_("Your hostname : %s") % system_setup.hostname)
        system_setup.micro_codes.print_resume()
        if system_setup.kernel:
            system_setup.kernel.print_resume()
        if system_setup.desktop:
            system_setup.desktop.print_resume()
        if system_setup.network:
            system_setup.network.print_resume()
        for bundle in system_setup.bundles:
            if bundle is not None and isinstance(bundle, Bundle):
                bundle.print_resume()
        print_sub_step(_("Your timezone : %s") % system_setup.timezone)
        if system_setup.user_name:
            print_sub_step(_("Additional user name : %s") % system_setup.user_name)
            if system_setup.user_full_name:
                print_sub_step(_("User's full name : %s") % system_setup.user_full_name)
        if system_setup.more_pkgs:
            print_sub_step(_("More packages to install : %s") % " ".join(system_setup.more_pkgs))
        user_answer = prompt_bool(_("Is the information correct ?"), default=False)
    return system_setup
