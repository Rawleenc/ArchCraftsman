# ArchCraftsman, The careful yet very fast Arch Linux Craftsman.
# Copyright (C) 2023 Rawleenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
The system setup module
"""
import json
import re
from urllib.request import urlopen
from archcraftsman.base import is_bios, print_step, print_sub_step, prompt_ln

from archcraftsman.bundles.bundle import Bundle
from archcraftsman.bundles.copyacm import CopyACM
from archcraftsman.bundles.cups import Cups
from archcraftsman.bundles.grmlzsh import GrmlZsh
from archcraftsman.bundles.grub import Grub
from archcraftsman.bundles.mainfilesystems import get_main_file_systems, MainFileSystems
from archcraftsman.bundles.mainfonts import get_main_fonts, MainFonts
from archcraftsman.bundles.microcodes import Microcodes
from archcraftsman.bundles.nvidia import NvidiaDriver
from archcraftsman.bundles.pipewire import PipeWire
from archcraftsman.bundles.terminus import TerminusFont
from archcraftsman.bundles.utils import prompt_bundle
from archcraftsman.bundles.zram import Zram
from archcraftsman.globalargs import GlobalArgs
from archcraftsman.globalinfo import GlobalInfo
from archcraftsman.i18n import I18n
from archcraftsman.options import (
    BundleTypes,
    Kernels,
    Desktops,
    Bundles,
    BootLoaders,
    Languages,
    Network,
)
from archcraftsman.packages import Packages
from archcraftsman.prelaunchinfo import parse_detected_language
from archcraftsman.utils import (
    ask_keymap,
    generate_translations,
    print_error,
    prompt_bool,
    ask_password,
    prompt_option,
)

_ = I18n().gettext


def initial_setup(shell_mode: bool = False):
    """
    The method to get environment configurations from the user.
    """
    print_sub_step(_("Querying IP geolocation information..."))
    with urlopen("https://ipapi.co/json") as response:
        geoip_info = json.loads(response.read())
    detected_language = str(geoip_info["languages"]).split(",", maxsplit=1)[0]
    detected_timezone = geoip_info["timezone"]

    default_language = parse_detected_language(detected_language)

    if detected_language == "fr-FR":
        default_keymap = "fr-latin9"
    else:
        default_keymap = "de-latin1"

    if not GlobalArgs().config():
        GlobalInfo().pre_launch_info.detected_timezone = detected_timezone
        GlobalInfo().pre_launch_info.global_language = default_language
        GlobalInfo().pre_launch_info.keymap = default_keymap

    user_answer = shell_mode or GlobalArgs().config()
    while not user_answer:
        print_step(_("Welcome to ArchCraftsman !"))
        if is_bios():
            print_error(
                _(
                    "BIOS detected ! The script will act accordingly. Don't forget to select a DOS label type before "
                    "partitioning."
                )
            )

        print_step(_("Environment configuration : "), clear=False)

        global_language = prompt_option(
            _("Choose your installation's language (%s) : "),
            _("Global language '%s' is not supported."),
            Languages,
            supported_msg=_("Supported languages : "),
            default=default_language,
        )
        if global_language:
            GlobalInfo().pre_launch_info.global_language = global_language

        GlobalInfo().pre_launch_info.keymap = ask_keymap(default_keymap)

        print_step(_("Summary of choices :"), clear=False)
        print_sub_step(
            _("Your installation's language : %s")
            % GlobalInfo().pre_launch_info.global_language
        )
        print_sub_step(
            _("Your installation's keymap : %s") % GlobalInfo().pre_launch_info.keymap
        )
        user_answer = prompt_bool(_("Is the information correct ?"), default=False)
    generate_translations(GlobalInfo().pre_launch_info.global_language)
    if not shell_mode:
        GlobalInfo().pre_launch_info.setup_locale()


def setup_system():
    """
    The method to get system configurations from the user.
    """
    user_answer = False
    while not user_answer:
        print_step(_("System configuration : "))
        GlobalInfo().system_info.hostname = prompt_ln(
            _("What will be your hostname (archlinux) : "), default="archlinux"
        )
        GlobalInfo().system_info.bundles = []

        GlobalInfo().system_info.bundles.append(
            prompt_bundle(
                _("Choose your kernel (%s) : "),
                _("Kernel '%s' is not supported."),
                Kernels,
                BundleTypes.KERNEL,
                _("Supported kernels : "),
                Kernels.CURRENT,
            )
        )

        GlobalInfo().system_info.bundles.append(
            prompt_bundle(
                _("Install a desktop environment ? (%s) : "),
                _("Desktop environment '%s' is not supported."),
                Desktops,
                BundleTypes.DESKTOP,
                _("Supported desktop environments : "),
                Desktops.NONE,
            )
        )

        GlobalInfo().system_info.bundles.append(
            prompt_bundle(
                _("Choose your network stack (%s) : "),
                _("Network stack '%s' is not supported."),
                Network,
                BundleTypes.NETWORK,
                _("Supported network stacks : "),
                Network.NETWORK_MANAGER,
            )
        )

        if prompt_bool(_("Install proprietary Nvidia driver ?"), default=False):
            GlobalInfo().system_info.bundles.append(
                NvidiaDriver(Bundles.NVIDIA, BundleTypes.OTHER)
            )

        if prompt_bool(_("Install terminus console font ?"), default=False):
            GlobalInfo().system_info.bundles.append(
                TerminusFont(Bundles.TERMINUS, BundleTypes.OTHER)
            )

        if prompt_bool(_("Install Cups ?"), default=False):
            GlobalInfo().system_info.bundles.append(
                Cups(Bundles.CUPS, BundleTypes.OTHER)
            )

        if prompt_bool(
            _("Install ZSH with GRML configuration ?"),
            default=False,
            help_msg=_(
                "If yes, the script will install the ZSH shell with GRML "
                "configuration. GRML is a ZSH pre-configuration used by Archlinux's "
                "live environment."
            ),
        ):
            GlobalInfo().system_info.bundles.append(
                GrmlZsh(Bundles.GRML, BundleTypes.OTHER)
            )

        if prompt_bool(
            _("Install a set of main fonts ?"),
            default=False,
            help_msg=_("If yes, the following packages will be installed :\n%s")
            % " ".join(get_main_fonts()),
        ):
            GlobalInfo().system_info.bundles.append(
                MainFonts(Bundles.MAIN_FONTS, BundleTypes.OTHER)
            )

        if prompt_bool(
            _("Install main file systems support ?"),
            default=False,
            help_msg=_("If yes, the following packages will be installed :\n%s")
            % " ".join(get_main_file_systems()),
        ):
            GlobalInfo().system_info.bundles.append(
                MainFileSystems(Bundles.MAIN_FILE_SYSTEMS, BundleTypes.OTHER)
            )

        if prompt_bool(
            _("Install and enable ZRAM ?"),
            default=False,
            help_msg=_(
                "ZRAM is a process to compress datas directly in the RAM instead of moving them in a swap. "
                "Enabled ZRAM will allow you to compress up to half of your RAM before having to swap. "
                "This method is more efficient than the swap and do not use your disk but is more CPU demanding. "
                "ZRAM is fully compatible with a swap, it just has a higher priority."
            ),
        ):
            GlobalInfo().system_info.bundles.append(
                Zram(Bundles.ZRAM, BundleTypes.OTHER)
            )

        if prompt_bool(
            _("Install PipeWire ?"),
            default=False,
            help_msg=_(
                "If yes, the PipeWire multimedia framework will be installed "
                "to manage audio and video capture."
            ),
        ):
            GlobalInfo().system_info.bundles.append(
                PipeWire(Bundles.PIPEWIRE, BundleTypes.OTHER)
            )

        if prompt_bool(_("Copy ArchCraftsman to the new system ?"), default=False):
            GlobalInfo().system_info.bundles.append(
                CopyACM(Bundles.COPY_ACM, BundleTypes.OTHER)
            )

        default_timezone_file = (
            f"/usr/share/zoneinfo/{GlobalInfo().pre_launch_info.detected_timezone}"
        )
        GlobalInfo().system_info.timezone = prompt_ln(
            _("Your timezone (%s) : ") % default_timezone_file,
            default=default_timezone_file,
        )
        user_name_pattern = re.compile("^[a-z][-a-z\\d_]*$")
        user_name_ok = False
        while not user_name_ok:
            GlobalInfo().system_info.user_name = prompt_ln(
                _(
                    "Would you like to add a user? (type username, leave blank if "
                    "none) : "
                )
            )
            if GlobalInfo().system_info.user_name and not user_name_pattern.match(
                GlobalInfo().system_info.user_name
            ):
                print_error(_("Invalid user name."))
                continue
            user_name_ok = True
        GlobalInfo().system_info.user_full_name = ""
        if GlobalInfo().system_info.user_name:
            GlobalInfo().system_info.user_full_name = prompt_ln(
                _(
                    "What is the %s's full name (type the entire full name, leave blank if none) : "
                )
                % GlobalInfo().system_info.user_name
            )

        GlobalInfo().system_info.more_pkgs = Packages().ask_packages()

        print_sub_step(_("%s password configuration : ") % "root")
        GlobalInfo().system_info.root_password = ask_password(
            _("Enter the %s password : ") % "root"
        )
        if GlobalInfo().system_info.user_name:
            print_sub_step(
                _("%s password configuration : ") % GlobalInfo().system_info.user_name
            )
            GlobalInfo().system_info.user_password = ask_password(
                _("Enter the %s password : ") % GlobalInfo().system_info.user_name
            )

        GlobalInfo().system_info.bundles.append(
            Grub(BootLoaders.GRUB, BundleTypes.BOOTLOADER)
        )
        GlobalInfo().system_info.bundles.append(
            Microcodes(Bundles.MICROCODES, BundleTypes.MICRO_CODES)
        )

        print_step(_("Summary of choices :"))
        print_sub_step(_("Your hostname : %s") % GlobalInfo().system_info.hostname)
        for bundle in GlobalInfo().system_info.bundles:
            if bundle is not None and isinstance(bundle, Bundle):
                bundle.print_resume()
        print_sub_step(_("Your timezone : %s") % GlobalInfo().system_info.timezone)
        if GlobalInfo().system_info.user_name:
            print_sub_step(
                _("Additional user name : %s") % GlobalInfo().system_info.user_name
            )
            if GlobalInfo().system_info.user_full_name:
                print_sub_step(
                    _("User's full name : %s") % GlobalInfo().system_info.user_full_name
                )
        if GlobalInfo().system_info.more_pkgs:
            print_sub_step(
                _("More packages to install : %s")
                % " ".join(GlobalInfo().system_info.more_pkgs)
            )
        user_answer = prompt_bool(_("Is the information correct ?"), default=False)
