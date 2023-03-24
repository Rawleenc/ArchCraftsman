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
The module of PreLaunchInfo class.
"""
import os

from archcraftsman.globalargs import GlobalArgs
from archcraftsman.i18n import I18n
from archcraftsman.utils import print_step, execute, log

_ = I18n().gettext


class PreLaunchInfo:
    """
    The class to contain all pre-launch information.
    """

    global_language: str
    keymap: str
    detected_timezone: str
    live_console_font: str

    def setup_locale(self):
        """
        The method to set up environment locale.
        """
        print_step(_("Configuring live environment..."), clear=False)
        self.live_console_font = "ter-v16b"
        if GlobalArgs().install():
            execute(f'loadkeys "{self.keymap}"')
            execute("setfont ter-v16b")
            dimensions = execute("stty size", capture_output=True).output
            if dimensions:
                split_dimensions = dimensions.split(" ")
                if (
                    split_dimensions
                    and len(split_dimensions) > 0
                    and int(split_dimensions[0]) >= 80
                ):
                    self.live_console_font = "ter-v32b"
                    execute("setfont ter-v32b")
        if self.global_language == "FR":
            if GlobalArgs().install():
                execute(
                    'sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /etc/locale.gen'
                )
                execute("locale-gen")
            os.putenv("LANG", "fr_FR.UTF-8")
            os.putenv("LANGUAGE", "fr_FR.UTF-8")
        else:
            os.putenv("LANG", "en_US.UTF-8")
            os.putenv("LANGUAGE", "en_US.UTF-8")

    def setup_chroot_keyboard(self):
        """
        The method to set the X keyboard of the chrooted system.
        """
        layout: str
        match self.keymap:
            case "fr-latin9":
                layout = "fr"
            case _:
                return
        content = [
            'Section "InputClass"\n',
            '    Identifier "system-keyboard"\n',
            '    MatchIsKeyboard "on"\n',
            f'    Option "XkbLayout" "{layout}"\n',
            "EndSection\n",
        ]
        execute("mkdir --parents /mnt/etc/X11/xorg.conf.d/")
        try:
            with open(
                "/mnt/etc/X11/xorg.conf.d/00-keyboard.conf", "w", encoding="UTF-8"
            ) as keyboard_config_file:
                keyboard_config_file.writelines(content)
        except FileNotFoundError as exception:
            log(f"Exception: {exception}")
