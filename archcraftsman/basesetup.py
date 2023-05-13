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
import subprocess
import sys
import urllib.request

import archcraftsman.arguments
import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.bundles.copyacm
import archcraftsman.bundles.genericbundle
import archcraftsman.bundles.grmlzsh
import archcraftsman.bundles.grub
import archcraftsman.bundles.microcodes
import archcraftsman.bundles.nvidia
import archcraftsman.bundles.terminus
import archcraftsman.bundles.utils
import archcraftsman.bundles.zram
import archcraftsman.config
import archcraftsman.i18n
import archcraftsman.info
import archcraftsman.options
import archcraftsman.packages
import archcraftsman.prelaunchinfo
import archcraftsman.utils

_ = archcraftsman.i18n.translate


def initial_setup(shell_mode: bool = False):
    """
    The method to get environment configurations from the user.
    """
    archcraftsman.base.print_sub_step(_("Querying IP geolocation information..."))
    with urllib.request.urlopen("https://ipapi.co/json") as response:
        geoip_info = json.loads(response.read())
    detected_language = str(geoip_info["languages"]).split(",", maxsplit=1)[0]
    detected_timezone = geoip_info["timezone"]

    default_language = archcraftsman.prelaunchinfo.parse_detected_language(
        detected_language
    )

    if detected_language == "fr-FR":
        default_keymap = "fr-latin9"
    else:
        default_keymap = "de-latin1"

    if not archcraftsman.arguments.config():
        archcraftsman.info.ai.pre_launch_info.detected_timezone = detected_timezone
        archcraftsman.info.ai.pre_launch_info.global_language = default_language
        archcraftsman.info.ai.pre_launch_info.keymap = default_keymap

    user_answer = shell_mode or archcraftsman.arguments.config()
    while not user_answer:
        archcraftsman.base.print_step(_("Welcome to ArchCraftsman !"))
        if archcraftsman.base.is_bios():
            archcraftsman.base.print_error(
                _(
                    "BIOS detected ! The script will act accordingly. Don't forget to select a DOS label type before "
                    "partitioning."
                )
            )

        archcraftsman.base.print_step(_("Environment configuration : "), clear=False)

        global_language = archcraftsman.utils.prompt_option(
            _("Choose your installation's language (%s) : "),
            _("Global language '%s' is not supported."),
            archcraftsman.options.Languages,
            supported_msg=_("Supported languages : "),
            default=default_language,
        )
        if global_language:
            archcraftsman.info.ai.pre_launch_info.global_language = global_language

        archcraftsman.info.ai.pre_launch_info.keymap = archcraftsman.utils.ask_keymap(
            default_keymap
        )

        archcraftsman.base.print_step(_("Summary of choices :"), clear=False)
        archcraftsman.base.print_sub_step(
            _("Your installation's language : %s")
            % archcraftsman.info.ai.pre_launch_info.global_language
        )
        archcraftsman.base.print_sub_step(
            _("Your installation's keymap : %s")
            % archcraftsman.info.ai.pre_launch_info.keymap
        )
        user_answer = archcraftsman.utils.prompt_bool(
            _("Is the information correct ?"), default=False
        )
    archcraftsman.utils.generate_translations(
        archcraftsman.info.ai.pre_launch_info.global_language
    )
    if not shell_mode:
        archcraftsman.info.ai.pre_launch_info.setup_locale()


def pre_launch(shell_mode: bool = False):
    """
    A pre-launch steps method.
    """
    try:
        if not archcraftsman.base.elevate():
            archcraftsman.base.print_error(
                _("This script must be run as root."), do_pause=False
            )
            sys.exit(1)

        if archcraftsman.arguments.config():
            archcraftsman.config.deserialize(archcraftsman.arguments.config())

        archcraftsman.base.print_step(_("Running pre-launch steps : "), clear=False)

        if not shell_mode:
            archcraftsman.base.execute('sed -i "s|#Color|Color|g" /etc/pacman.conf')
            archcraftsman.base.execute(
                'sed -i "s|#ParallelDownloads = 5|ParallelDownloads = 5\\nDisableDownloadTimeout|g" /etc/pacman.conf'
            )

            archcraftsman.base.print_sub_step(_("Synchronising repositories..."))
            archcraftsman.base.execute("pacman -Sy &>/dev/null")
            archcraftsman.packages.Packages()

        initial_setup(shell_mode)
    except KeyboardInterrupt:
        archcraftsman.base.print_error(
            _("Script execution interrupted by the user !"), do_pause=False
        )
        sys.exit(1)
    except subprocess.CalledProcessError as exception:
        archcraftsman.base.print_error(
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
        archcraftsman.base.print_step(_("System configuration : "))
        archcraftsman.info.ai.system_info.hostname = archcraftsman.base.prompt_ln(
            _("What will be your hostname (archlinux) : "), default="archlinux"
        )
        archcraftsman.info.ai.system_info.bundles = []

        archcraftsman.info.ai.system_info.bundles.append(
            archcraftsman.bundles.utils.prompt_bundle(
                _("Choose your kernel (%s) : "),
                _("Kernel '%s' is not supported."),
                archcraftsman.options.Kernels,
                _("Supported kernels : "),
                archcraftsman.options.Kernels.CURRENT,
            )
        )

        archcraftsman.info.ai.system_info.bundles.append(
            archcraftsman.bundles.utils.prompt_bundle(
                _("Install a desktop environment ? (%s) : "),
                _("Desktop environment '%s' is not supported."),
                archcraftsman.options.Desktops,
                _("Supported desktop environments : "),
                archcraftsman.options.Desktops.NONE,
            )
        )

        archcraftsman.info.ai.system_info.bundles.append(
            archcraftsman.bundles.utils.prompt_bundle(
                _("Choose your network stack (%s) : "),
                _("Network stack '%s' is not supported."),
                archcraftsman.options.Network,
                _("Supported network stacks : "),
                archcraftsman.options.Network.NETWORK_MANAGER,
            )
        )

        if archcraftsman.utils.prompt_bool(
            _("Install proprietary Nvidia driver ?"), default=False
        ):
            archcraftsman.info.ai.system_info.bundles.append(
                archcraftsman.bundles.nvidia.NvidiaDriver()
            )

        if archcraftsman.utils.prompt_bool(
            _("Install terminus console font ?"), default=False
        ):
            archcraftsman.info.ai.system_info.bundles.append(
                archcraftsman.bundles.terminus.TerminusFont()
            )

        if archcraftsman.utils.prompt_bool(
            _("Install ZSH with GRML configuration ?"),
            default=False,
            help_msg=_(
                "If yes, the script will install the ZSH shell with GRML "
                "configuration. GRML is a ZSH pre-configuration used by Archlinux's "
                "live environment."
            ),
        ):
            archcraftsman.info.ai.system_info.bundles.append(
                archcraftsman.bundles.grmlzsh.GrmlZsh()
            )

        if archcraftsman.utils.prompt_bool(
            _("Install and enable ZRAM ?"),
            default=False,
            help_msg=_(
                "ZRAM is a process to compress datas directly in the RAM instead of moving them in a swap. "
                "Enabled ZRAM will allow you to compress up to half of your RAM before having to swap. "
                "This method is more efficient than the swap and do not use your disk but is more CPU demanding. "
                "ZRAM is fully compatible with a swap, it just has a higher priority."
            ),
        ):
            archcraftsman.info.ai.system_info.bundles.append(
                archcraftsman.bundles.zram.Zram()
            )

        if archcraftsman.utils.prompt_bool(
            _("Copy ArchCraftsman to the new system ?"), default=False
        ):
            archcraftsman.info.ai.system_info.bundles.append(
                archcraftsman.bundles.copyacm.CopyACM()
            )

        for generic_bundle_name in archcraftsman.bundles.utils.list_generic_bundles():
            generic_bundle = archcraftsman.bundles.genericbundle.GenericBundle(
                generic_bundle_name
            )
            if archcraftsman.utils.prompt_bool(
                generic_bundle.prompt(), default=False, help_msg=generic_bundle.help()
            ):
                archcraftsman.info.ai.system_info.bundles.append(generic_bundle)

        default_timezone_file = f"/usr/share/zoneinfo/{archcraftsman.info.ai.pre_launch_info.detected_timezone}"
        archcraftsman.info.ai.system_info.timezone = archcraftsman.base.prompt_ln(
            _("Your timezone (%s) : ") % default_timezone_file,
            default=default_timezone_file,
        )
        user_name_pattern = re.compile("^[a-z][-a-z\\d_]*$")
        user_name_ok = False
        while not user_name_ok:
            archcraftsman.info.ai.system_info.user_name = archcraftsman.base.prompt_ln(
                _(
                    "Would you like to add a user? (type username, leave blank if "
                    "none) : "
                )
            )
            if (
                archcraftsman.info.ai.system_info.user_name
                and not user_name_pattern.match(
                    archcraftsman.info.ai.system_info.user_name
                )
            ):
                archcraftsman.base.print_error(_("Invalid user name."))
                continue
            user_name_ok = True
        archcraftsman.info.ai.system_info.user_full_name = ""
        if archcraftsman.info.ai.system_info.user_name:
            archcraftsman.info.ai.system_info.user_full_name = archcraftsman.base.prompt_ln(
                _(
                    "What is the %s's full name (type the entire full name, leave blank if none) : "
                )
                % archcraftsman.info.ai.system_info.user_name
            )

        archcraftsman.info.ai.system_info.more_pkgs = (
            archcraftsman.packages.Packages().ask_packages()
        )

        archcraftsman.base.print_sub_step(_("%s password configuration : ") % "root")
        archcraftsman.info.ai.system_info.root_password = (
            archcraftsman.utils.ask_password(_("Enter the %s password : ") % "root")
        )
        if archcraftsman.info.ai.system_info.user_name:
            archcraftsman.base.print_sub_step(
                _("%s password configuration : ")
                % archcraftsman.info.ai.system_info.user_name
            )
            archcraftsman.info.ai.system_info.user_password = (
                archcraftsman.utils.ask_password(
                    _("Enter the %s password : ")
                    % archcraftsman.info.ai.system_info.user_name
                )
            )

        archcraftsman.info.ai.system_info.bundles.append(
            archcraftsman.bundles.grub.Grub()
        )
        archcraftsman.info.ai.system_info.bundles.append(
            archcraftsman.bundles.microcodes.Microcodes()
        )

        archcraftsman.base.print_step(_("Summary of choices :"))
        archcraftsman.base.print_sub_step(
            _("Your hostname : %s") % archcraftsman.info.ai.system_info.hostname
        )
        for bundle in archcraftsman.info.ai.system_info.bundles:
            if bundle is not None and isinstance(
                bundle, archcraftsman.bundles.bundle.Bundle
            ):
                bundle.print_resume()
        archcraftsman.base.print_sub_step(
            _("Your timezone : %s") % archcraftsman.info.ai.system_info.timezone
        )
        if archcraftsman.info.ai.system_info.user_name:
            archcraftsman.base.print_sub_step(
                _("Additional user name : %s")
                % archcraftsman.info.ai.system_info.user_name
            )
            if archcraftsman.info.ai.system_info.user_full_name:
                archcraftsman.base.print_sub_step(
                    _("User's full name : %s")
                    % archcraftsman.info.ai.system_info.user_full_name
                )
        if archcraftsman.info.ai.system_info.more_pkgs:
            archcraftsman.base.print_sub_step(
                _("More packages to install : %s")
                % " ".join(archcraftsman.info.ai.system_info.more_pkgs)
            )
        user_answer = archcraftsman.utils.prompt_bool(
            _("Is the information correct ?"), default=False
        )
