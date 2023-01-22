"""
LICENSE
ArchCraftsman, The careful yet very fast Arch Linux Craftsman.
Copyright (C) 2022  Rawleenc

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

DISCLAIMER
ArchCraftsman  Copyright (C) 2022  Rawleenc

This program comes with ABSOLUTELY NO WARRANTY; See the
GNU General Public License for more details.

This is free software, and you are welcome to redistribute it
under certain conditions; See the GNU General Public License for more details.
"""
import argparse
import glob
import json
import readline
import sys
from subprocess import CalledProcessError
from urllib.request import urlopen

from src.envsetup import setup_environment
from src.globalargs import GlobalArgs
from src.i18n import I18n
from src.installer import install
from src.localesetup import setup_locale
from src.shell import shell
from src.utils import print_error, execute, stdout, print_step, print_sub_step


def pre_launch_steps() -> {}:
    """
    The method to proceed to the pre-launch steps
    :return:
    """
    print_step(_("Running pre-launch steps : "), clear=False)
    execute('msgfmt -o /usr/share/locale/fr/LC_MESSAGES/ArchCraftsman.mo locales/fr.po &>/dev/null', force=True)
    if GlobalArgs().install():
        execute('sed -i "s|#Color|Color|g" /etc/pacman.conf')
        execute('sed -i "s|#ParallelDownloads = 5|ParallelDownloads = 5\\nDisableDownloadTimeout|g" /etc/pacman.conf')

    if GlobalArgs().install():
        print_sub_step(_("Synchronising repositories and keyring..."))
        execute("pacman --noconfirm -Sy --needed archlinux-keyring &>/dev/null")

    print_sub_step(_("Querying IP geolocation informations..."))
    with urlopen("https://ipapi.co/json") as response:
        geoip_info = json.loads(response.read())
    detected_language = str(geoip_info["languages"]).split(",", maxsplit=1)[0]
    detected_timezone = geoip_info["timezone"]
    pre_launch_info = setup_environment(detected_language)
    pre_launch_info["detected_timezone"] = detected_timezone
    pre_launch_info["live_console_font"] = setup_locale(keymap=pre_launch_info["keymap"],
                                                        global_language=pre_launch_info["global_language"])
    return pre_launch_info


def pre_launch() -> {}:
    """
    A pre-launch steps method.
    :return:
    """
    try:
        return pre_launch_steps()
    except KeyboardInterrupt:
        print_error(_("Script execution interrupted by the user !"), do_pause=False)
        sys.exit(1)
    except CalledProcessError as exception:
        print_error(_("A subprocess execution failed ! See the following error: %s") % exception, do_pause=False)
        sys.exit(1)
    except EOFError:
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="The ArchCraftsman installer.")
    parser.add_argument("-i", "--install", action="store_const", const=True, default=False,
                        help="Process to ArchLinux installation. Must be used in a live environment.")
    parser.add_argument("-s", "--shell", action="store_const", const=True, default=False,
                        help="Start ArchCraftsman in interactive shell mode. Useless if used with --install.")
    parser.add_argument("-t", "--test", action="store_const", const=True, default=False,
                        help="Used to test the installer. No command will be executed.")
    args = parser.parse_args()

    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(lambda text, state: (glob.glob(text + '*') + [None])[state])

    i18n = I18n()
    _ = i18n.gettext
    GlobalArgs(args)

    user = stdout(execute("whoami", capture_output=True, force=True))
    if not user or user.strip() != "root":
        print_error("This script must be run as root.")
        sys.exit(1)

    PRE_LAUNCH_INFO = pre_launch()
    _ = i18n.update_method(PRE_LAUNCH_INFO["global_language"])

    if GlobalArgs().install():
        install(PRE_LAUNCH_INFO)
        sys.exit(0)

    if GlobalArgs().shell():
        shell()
        sys.exit(0)

    parser.print_help()
