import os
import re

from src.bundles.bundle import Bundle
from src.bundles.cups import Cups
from src.bundles.grmlzsh import GrmlZsh
from src.bundles.grub import Grub
from src.bundles.i18n import I18n
from src.bundles.mainfilesystems import get_main_file_systems, MainFileSystems
from src.bundles.mainfonts import get_main_fonts, MainFonts
from src.bundles.microcodes import Microcodes
from src.bundles.nvidia import NvidiaDriver
from src.bundles.pipewire import PipeWire
from src.bundles.terminus import TerminusFont
from src.utils import print_step, is_bios, print_error, print_sub_step, prompt_ln, prompt_bool, prompt_bundle, \
    get_supported_kernels, get_supported_desktop_environments, ask_password
from src.bundles.zram import Zram

_ = I18n().gettext

def setup_locale(keymap: str = "de-latin1", global_language: str = "EN") -> str:
    """
    The method to setup environment locale.
    :param keymap:
    :param global_language:
    :return: The configured live system console font (terminus 16 or 32)
    """
    print_step(_("Configuring live environment..."), clear=False)
    os.system(f'loadkeys "{keymap}"')
    font = 'ter-v16b'
    os.system('setfont ter-v16b')
    dimensions = os.popen('stty size').read().split(" ")
    if dimensions and len(dimensions) > 0 and int(dimensions[0]) >= 80:
        font = 'ter-v32b'
        os.system('setfont ter-v32b')
    if global_language == "FR":
        os.system('sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /etc/locale.gen')
        os.system('locale-gen')
        os.putenv('LANG', 'fr_FR.UTF-8')
        os.putenv('LANGUAGE', 'fr_FR.UTF-8')
    else:
        os.putenv('LANG', 'en_US.UTF-8')
        os.putenv('LANGUAGE', 'en_US.UTF-8')
    return font


def setup_chroot_keyboard(layout: str):
    """
    The method to set the X keyboard of the chrooted system.
    :param layout:
    """
    content = [
        "Section \"InputClass\"\n",
        "    Identifier \"system-keyboard\"\n",
        "    MatchIsKeyboard \"on\"\n",
        f"    Option \"XkbLayout\" \"{layout}\"\n",
        "EndSection\n"
    ]
    os.system("mkdir --parents /mnt/etc/X11/xorg.conf.d/")
    with open("/mnt/etc/X11/xorg.conf.d/00-keyboard.conf", "w", encoding="UTF-8") as keyboard_config_file:
        keyboard_config_file.writelines(content)


def setup_environment(detected_language: str) -> {}:
    """
    The method to get environment configurations from the user.
    :param detected_language:
    :return:
    """
    pre_launch_info = {"global_language": None, "keymap": None}
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
        pre_launch_info["global_language"] = None
        pre_launch_info["keymap"] = None
        while not global_language_ok:
            pre_launch_info["global_language"] = prompt_ln(
                _("Choose your installation's language (%s) : ") % default_language,
                default=default_language).upper()
            if pre_launch_info["global_language"] in supported_global_languages:
                global_language_ok = True
            else:
                print_error(_("Global language '%s' is not supported.") % pre_launch_info["global_language"],
                            do_pause=False)
                continue

        if detected_language == "fr-FR":
            default_keymap = "fr-latin9"
        else:
            default_keymap = "de-latin1"

        keymap_ok = False
        while not keymap_ok:
            pre_launch_info["keymap"] = prompt_ln(_("Type your installation's keymap (%s) : ") % default_keymap,
                                                  default=default_keymap)
            if os.system(f'localectl list-keymaps | grep "^{pre_launch_info["keymap"]}$" &>/dev/null') == 0:
                keymap_ok = True
            else:
                print_error(_("Keymap %s doesn't exist.") % pre_launch_info["keymap"])
                continue

        print_step(_("Summary of choices :"), clear=False)
        print_sub_step(_("Your installation's language : %s") % pre_launch_info["global_language"])
        print_sub_step(_("Your installation's keymap : %s") % pre_launch_info["keymap"])
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
    return pre_launch_info


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

        system_info["kernel"] = prompt_bundle(_("Supported kernels : "),
                                              _("Choose your kernel (%s) : "),
                                              _("Kernel '%s' is not supported."),
                                              get_supported_kernels(get_default=True),
                                              get_supported_kernels())

        if prompt_bool(_("Install proprietary Nvidia driver ? (y/N) : "), default=False):
            system_info["bundles"].append(NvidiaDriver("nvidia"))

        if prompt_bool(_("Install terminus console font ? (y/N) : "), default=False):
            system_info["bundles"].append(TerminusFont("terminus"))

        system_info["bundles"].append(prompt_bundle(_("Supported desktop environments : "),
                                                    _("Install a desktop environment ? (%s) : "),
                                                    _("Desktop environment '%s' is not supported."),
                                                    get_supported_desktop_environments(get_default=True),
                                                    get_supported_desktop_environments()))

        if prompt_bool(_("Install Cups ? (y/N) : "), default=False):
            system_info["bundles"].append(Cups("cups"))

        if prompt_bool(_("Install ZSH with GRML configuration ? (y/N/?) : "), default=False,
                       help_msg=_(
                           "If yes, the script will install the ZSH shell with GRML "
                           "configuration. GRML is a ZSH pre-configuration used by Archlinux's "
                           "live environment.")):
            system_info["bundles"].append(GrmlZsh("grml"))

        if prompt_bool(_("Install a set of main fonts ? (y/N/?) : "), default=False,
                       help_msg=_("If yes, the following packages will be installed :\n%s") % " ".join(
                           get_main_fonts())):
            system_info["bundles"].append(MainFonts("mainfonts"))

        if prompt_bool(_("Install main file systems support ? (y/N/?) : "),
                       default=False, help_msg=_(
                    "If yes, the following packages will be installed :\n%s") % " ".join(get_main_file_systems())):
            system_info["bundles"].append(MainFileSystems("mainfilesystems"))

        if prompt_bool(_("Install and enable ZRAM ? (y/N/?) : "), default=False, help_msg=_(
                "ZRAM is a process to compress datas directly in the RAM instead of moving them in a swap. "
                "Enabled ZRAM will allow you to compress up to half of your RAM before having to swap. "
                "This method is more efficient than the swap and do not use your disk but is more CPU demanding. "
                "ZRAM is fully compatible with a swap, it just has a higher priority.")):
            system_info["bundles"].append(Zram("zram"))

        if prompt_bool(_("Install PipeWire ? (y/N/?) : "),
                       default=False, help_msg=_(
                    "If yes, the PipeWire multimedia framework will be installed to manage audio and video capture.")):
            system_info["bundles"].append(PipeWire("pipewire"))

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
                    if os.system(f'pacman -Si {pkg} &>/dev/null') != 0:
                        pkgs_select_ok = False
                        print_error(_("Package %s doesn't exist.") % pkg)
                        break
                    system_info["more_pkgs"].add(pkg)

        system_info["root_password"] = ask_password()
        if system_info["user_name"] != "":
            system_info["user_password"] = ask_password(system_info["user_name"])

        system_info["bootloader"] = Grub("grub")
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
