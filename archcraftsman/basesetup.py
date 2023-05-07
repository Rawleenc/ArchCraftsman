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
import sys
from subprocess import CalledProcessError
from urllib.request import urlopen

from archcraftsman import arguments, info
from archcraftsman.base import (
    elevate,
    execute,
    is_bios,
    print_error,
    print_step,
    print_sub_step,
    prompt_ln,
)
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.bundles.copyacm import CopyACM
from archcraftsman.bundles.grmlzsh import GrmlZsh
from archcraftsman.bundles.grub import Grub
from archcraftsman.bundles.mainfilesystems import MainFileSystems, get_main_file_systems
from archcraftsman.bundles.mainfonts import MainFonts, get_main_fonts
from archcraftsman.bundles.microcodes import Microcodes
from archcraftsman.bundles.nvidia import NvidiaDriver
from archcraftsman.bundles.pipewire import PipeWire
from archcraftsman.bundles.terminus import TerminusFont
from archcraftsman.bundles.utils import (
    list_generic_bundles,
    new_generic_bundle,
    prompt_bundle,
)
from archcraftsman.bundles.zram import Zram
from archcraftsman.config import deserialize
from archcraftsman.i18n import _
from archcraftsman.options import (
    BootLoaders,
    Bundles,
    Desktops,
    Kernels,
    Languages,
    Network,
)
from archcraftsman.packages import Packages
from archcraftsman.prelaunchinfo import parse_detected_language
from archcraftsman.utils import (
    ask_keymap,
    ask_password,
    generate_translations,
    prompt_bool,
    prompt_option,
)


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

    if not arguments.config():
        info.ai.pre_launch_info.detected_timezone = detected_timezone
        info.ai.pre_launch_info.global_language = default_language
        info.ai.pre_launch_info.keymap = default_keymap

    user_answer = shell_mode or arguments.config()
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
            info.ai.pre_launch_info.global_language = global_language

        info.ai.pre_launch_info.keymap = ask_keymap(default_keymap)

        print_step(_("Summary of choices :"), clear=False)
        print_sub_step(
            _("Your installation's language : %s")
            % info.ai.pre_launch_info.global_language
        )
        print_sub_step(
            _("Your installation's keymap : %s") % info.ai.pre_launch_info.keymap
        )
        user_answer = prompt_bool(_("Is the information correct ?"), default=False)
    generate_translations(info.ai.pre_launch_info.global_language)
    if not shell_mode:
        info.ai.pre_launch_info.setup_locale()


def pre_launch(shell_mode: bool = False):
    """
    A pre-launch steps method.
    """
    try:
        if not elevate():
            print_error(_("This script must be run as root."), do_pause=False)
            sys.exit(1)

        if arguments.config():
            deserialize(arguments.config())

        print_step(_("Running pre-launch steps : "), clear=False)

        if not shell_mode:
            execute('sed -i "s|#Color|Color|g" /etc/pacman.conf')
            execute(
                'sed -i "s|#ParallelDownloads = 5|ParallelDownloads = 5\\nDisableDownloadTimeout|g" /etc/pacman.conf'
            )

            print_sub_step(_("Synchronising repositories..."))
            execute("pacman -Sy &>/dev/null")
            Packages()

        initial_setup(shell_mode)
    except KeyboardInterrupt:
        print_error(_("Script execution interrupted by the user !"), do_pause=False)
        sys.exit(1)
    except CalledProcessError as exception:
        print_error(
            _("A subprocess execution failed ! See the following error: %s")
            % exception,
            do_pause=False,
        )
        sys.exit(1)
    except EOFError:
        sys.exit(1)


def setup_system():
    """
    The method to get system configurations from the user.
    """
    user_answer = False
    while not user_answer:
        print_step(_("System configuration : "))
        info.ai.system_info.hostname = prompt_ln(
            _("What will be your hostname (archlinux) : "), default="archlinux"
        )
        info.ai.system_info.bundles = []

        info.ai.system_info.bundles.append(
            prompt_bundle(
                _("Choose your kernel (%s) : "),
                _("Kernel '%s' is not supported."),
                Kernels,
                _("Supported kernels : "),
                Kernels.CURRENT,
            )
        )

        info.ai.system_info.bundles.append(
            prompt_bundle(
                _("Install a desktop environment ? (%s) : "),
                _("Desktop environment '%s' is not supported."),
                Desktops,
                _("Supported desktop environments : "),
                Desktops.NONE,
            )
        )

        info.ai.system_info.bundles.append(
            prompt_bundle(
                _("Choose your network stack (%s) : "),
                _("Network stack '%s' is not supported."),
                Network,
                _("Supported network stacks : "),
                Network.NETWORK_MANAGER,
            )
        )

        if prompt_bool(_("Install proprietary Nvidia driver ?"), default=False):
            info.ai.system_info.bundles.append(NvidiaDriver(Bundles.NVIDIA))

        if prompt_bool(_("Install terminus console font ?"), default=False):
            info.ai.system_info.bundles.append(TerminusFont(Bundles.TERMINUS))

        if prompt_bool(
            _("Install ZSH with GRML configuration ?"),
            default=False,
            help_msg=_(
                "If yes, the script will install the ZSH shell with GRML "
                "configuration. GRML is a ZSH pre-configuration used by Archlinux's "
                "live environment."
            ),
        ):
            info.ai.system_info.bundles.append(GrmlZsh(Bundles.GRML))

        if prompt_bool(
            _("Install a set of main fonts ?"),
            default=False,
            help_msg=_("If yes, the following packages will be installed :\n%s")
            % " ".join(get_main_fonts()),
        ):
            info.ai.system_info.bundles.append(MainFonts(Bundles.MAIN_FONTS))

        if prompt_bool(
            _("Install main file systems support ?"),
            default=False,
            help_msg=_("If yes, the following packages will be installed :\n%s")
            % " ".join(get_main_file_systems()),
        ):
            info.ai.system_info.bundles.append(
                MainFileSystems(Bundles.MAIN_FILE_SYSTEMS)
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
            info.ai.system_info.bundles.append(Zram(Bundles.ZRAM))

        if prompt_bool(
            _("Install PipeWire ?"),
            default=False,
            help_msg=_(
                "If yes, the PipeWire multimedia framework will be installed "
                "to manage audio and video capture."
            ),
        ):
            info.ai.system_info.bundles.append(PipeWire(Bundles.PIPEWIRE))

        if prompt_bool(_("Copy ArchCraftsman to the new system ?"), default=False):
            info.ai.system_info.bundles.append(CopyACM(Bundles.COPY_ACM))

        for generic_bundle_name in list_generic_bundles():
            generic_bundle = new_generic_bundle(generic_bundle_name)
            if prompt_bool(
                generic_bundle.prompt(), default=False, help_msg=generic_bundle.help()
            ):
                info.ai.system_info.bundles.append(generic_bundle)

        default_timezone_file = (
            f"/usr/share/zoneinfo/{info.ai.pre_launch_info.detected_timezone}"
        )
        info.ai.system_info.timezone = prompt_ln(
            _("Your timezone (%s) : ") % default_timezone_file,
            default=default_timezone_file,
        )
        user_name_pattern = re.compile("^[a-z][-a-z\\d_]*$")
        user_name_ok = False
        while not user_name_ok:
            info.ai.system_info.user_name = prompt_ln(
                _(
                    "Would you like to add a user? (type username, leave blank if "
                    "none) : "
                )
            )
            if info.ai.system_info.user_name and not user_name_pattern.match(
                info.ai.system_info.user_name
            ):
                print_error(_("Invalid user name."))
                continue
            user_name_ok = True
        info.ai.system_info.user_full_name = ""
        if info.ai.system_info.user_name:
            info.ai.system_info.user_full_name = prompt_ln(
                _(
                    "What is the %s's full name (type the entire full name, leave blank if none) : "
                )
                % info.ai.system_info.user_name
            )

        info.ai.system_info.more_pkgs = Packages().ask_packages()

        print_sub_step(_("%s password configuration : ") % "root")
        info.ai.system_info.root_password = ask_password(
            _("Enter the %s password : ") % "root"
        )
        if info.ai.system_info.user_name:
            print_sub_step(
                _("%s password configuration : ") % info.ai.system_info.user_name
            )
            info.ai.system_info.user_password = ask_password(
                _("Enter the %s password : ") % info.ai.system_info.user_name
            )

        info.ai.system_info.bundles.append(Grub(BootLoaders.GRUB))
        info.ai.system_info.bundles.append(Microcodes(Bundles.MICROCODES))

        print_step(_("Summary of choices :"))
        print_sub_step(_("Your hostname : %s") % info.ai.system_info.hostname)
        for bundle in info.ai.system_info.bundles:
            if bundle is not None and isinstance(bundle, Bundle):
                bundle.print_resume()
        print_sub_step(_("Your timezone : %s") % info.ai.system_info.timezone)
        if info.ai.system_info.user_name:
            print_sub_step(
                _("Additional user name : %s") % info.ai.system_info.user_name
            )
            if info.ai.system_info.user_full_name:
                print_sub_step(
                    _("User's full name : %s") % info.ai.system_info.user_full_name
                )
        if info.ai.system_info.more_pkgs:
            print_sub_step(
                _("More packages to install : %s")
                % " ".join(info.ai.system_info.more_pkgs)
            )
        user_answer = prompt_bool(_("Is the information correct ?"), default=False)
