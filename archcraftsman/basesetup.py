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
import re

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
from archcraftsman.i18n import I18n
from archcraftsman.options import Kernels, Desktops, Bundles, BootLoaders, Network
from archcraftsman.packages import Packages
from archcraftsman.prelaunchinfo import PreLaunchInfo
from archcraftsman.systeminfo import SystemInfo
from archcraftsman.utils import (
    print_error,
    print_step,
    print_sub_step,
    prompt_ln,
    prompt_bool,
    ask_password,
    execute,
    is_bios,
)

_ = I18n().gettext


def initial_setup(detected_language: str, detected_timezone: str) -> PreLaunchInfo:
    """
    The method to get environment configurations from the user.
    """
    pre_launch_info = PreLaunchInfo()
    user_answer = False
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

        supported_global_languages = ["FR", "EN"]
        if detected_language == "fr-FR":
            default_language = "FR"
        else:
            default_language = "EN"

        print_step(_("Supported languages : "), clear=False)
        print_sub_step(", ".join(supported_global_languages))
        print("")
        global_language_ok = False
        pre_launch_info.global_language = ""
        pre_launch_info.keymap = ""
        while not global_language_ok:
            pre_launch_info.global_language = prompt_ln(
                _("Choose your installation's language (%s) : ") % default_language,
                default=default_language,
            ).upper()
            if pre_launch_info.global_language in supported_global_languages:
                global_language_ok = True
            else:
                print_error(
                    _("Global language '%s' is not supported.")
                    % pre_launch_info.global_language,
                    do_pause=False,
                )
                continue

        if detected_language == "fr-FR":
            default_keymap = "fr-latin9"
        else:
            default_keymap = "de-latin1"

        keymap_ok = False
        while not keymap_ok:
            pre_launch_info.keymap = prompt_ln(
                _("Type your installation's keymap (%s) : ") % default_keymap,
                default=default_keymap,
            )
            if execute(
                f'localectl list-keymaps | grep "^{pre_launch_info.keymap}$" &>/dev/null'
            ):
                keymap_ok = True
            else:
                print_error(_("Keymap %s doesn't exist.") % pre_launch_info.keymap)
                continue

        print_step(_("Summary of choices :"), clear=False)
        print_sub_step(
            _("Your installation's language : %s") % pre_launch_info.global_language
        )
        print_sub_step(_("Your installation's keymap : %s") % pre_launch_info.keymap)
        user_answer = prompt_bool(_("Is the information correct ?"), default=False)
    pre_launch_info.detected_timezone = detected_timezone
    pre_launch_info.setup_locale()
    return pre_launch_info


def setup_system(detected_timezone) -> SystemInfo:
    """
    The method to get system configurations from the user.
    """
    system_setup = SystemInfo()
    user_answer = False
    while not user_answer:
        print_step(_("System configuration : "))
        system_setup.hostname = prompt_ln(
            _("What will be your hostname (archlinux) : "), default="archlinux"
        )
        system_setup.bundles = []

        system_setup.kernel = prompt_bundle(
            _("Choose your kernel (%s) : "),
            _("Kernel '%s' is not supported."),
            Kernels,
            _("Supported kernels : "),
            Kernels.CURRENT,
        )

        system_setup.desktop = prompt_bundle(
            _("Install a desktop environment ? (%s) : "),
            _("Desktop environment '%s' is not supported."),
            Desktops,
            _("Supported desktop environments : "),
            Desktops.NONE,
        )

        system_setup.network = prompt_bundle(
            _("Choose your network stack (%s) : "),
            _("Network stack '%s' is not supported."),
            Network,
            _("Supported network stacks : "),
            Network.NETWORK_MANAGER,
        )

        if prompt_bool(_("Install proprietary Nvidia driver ?"), default=False):
            system_setup.bundles.append(NvidiaDriver(Bundles.NVIDIA))

        if prompt_bool(_("Install terminus console font ?"), default=False):
            system_setup.bundles.append(TerminusFont(Bundles.TERMINUS))

        if prompt_bool(_("Install Cups ?"), default=False):
            system_setup.bundles.append(Cups(Bundles.CUPS))

        if prompt_bool(
            _("Install ZSH with GRML configuration ?"),
            default=False,
            help_msg=_(
                "If yes, the script will install the ZSH shell with GRML "
                "configuration. GRML is a ZSH pre-configuration used by Archlinux's "
                "live environment."
            ),
        ):
            system_setup.bundles.append(GrmlZsh(Bundles.GRML))

        if prompt_bool(
            _("Install a set of main fonts ?"),
            default=False,
            help_msg=_("If yes, the following packages will be installed :\n%s")
            % " ".join(get_main_fonts()),
        ):
            system_setup.bundles.append(MainFonts(Bundles.MAIN_FONTS))

        if prompt_bool(
            _("Install main file systems support ?"),
            default=False,
            help_msg=_("If yes, the following packages will be installed :\n%s")
            % " ".join(get_main_file_systems()),
        ):
            system_setup.bundles.append(MainFileSystems(Bundles.MAIN_FILE_SYSTEMS))

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
            system_setup.bundles.append(Zram(Bundles.ZRAM))

        if prompt_bool(
            _("Install PipeWire ?"),
            default=False,
            help_msg=_(
                "If yes, the PipeWire multimedia framework will be installed "
                "to manage audio and video capture."
            ),
        ):
            system_setup.bundles.append(PipeWire(Bundles.PIPEWIRE))

        if prompt_bool(_("Copy ArchCraftsman to the new system ?"), default=False):
            system_setup.bundles.append(CopyACM(Bundles.COPY_ACM))

        default_timezone_file = f"/usr/share/zoneinfo/{detected_timezone}"
        system_setup.timezone = prompt_ln(
            _("Your timezone (%s) : ") % default_timezone_file,
            default=default_timezone_file,
        )
        user_name_pattern = re.compile("^[a-z][-a-z\\d_]*$")
        user_name_ok = False
        while not user_name_ok:
            system_setup.user_name = prompt_ln(
                _(
                    "Would you like to add a user? (type username, leave blank if "
                    "none) : "
                )
            )
            if system_setup.user_name and not user_name_pattern.match(
                system_setup.user_name
            ):
                print_error(_("Invalid user name."))
                continue
            user_name_ok = True
        system_setup.user_full_name = ""
        if system_setup.user_name:
            system_setup.user_full_name = prompt_ln(
                _(
                    "What is the %s's full name (type the entire full name, leave blank if none) : "
                )
                % system_setup.user_name
            )

        system_setup.more_pkgs = Packages().ask_packages()

        print_sub_step(_("%s password configuration : ") % "root")
        system_setup.root_password = ask_password(
            _("Enter the %s password : ") % "root"
        )
        if system_setup.user_name:
            print_sub_step(_("%s password configuration : ") % system_setup.user_name)
            system_setup.user_password = ask_password(
                _("Enter the %s password : ") % system_setup.user_name
            )

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
            print_sub_step(
                _("More packages to install : %s") % " ".join(system_setup.more_pkgs)
            )
        user_answer = prompt_bool(_("Is the information correct ?"), default=False)
    return system_setup
