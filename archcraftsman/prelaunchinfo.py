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
import json
import os
import urllib.request

import archcraftsman.base
import archcraftsman.i18n
import archcraftsman.options

_ = archcraftsman.i18n.translate


DEFAULT_KEYMAP = "de-latin1"


DEFAULT_KEYMAPS = {
    archcraftsman.options.Languages.FRENCH: "fr-latin9",
}


def parse_detected_language(detected_language: str) -> archcraftsman.options.Languages:
    """
    The function to parse the detected language.
    """
    match detected_language:
        case "fr-FR":
            return archcraftsman.options.Languages.FRENCH
        case _:
            return archcraftsman.options.Languages.ENGLISH


def get_default_keymap(
    language: archcraftsman.options.Languages, detected_country_code: str
) -> str:
    """
    The function to get the default keymap for a language.
    """
    if language in DEFAULT_KEYMAPS:
        return DEFAULT_KEYMAPS[language]

    lower_country_code = detected_country_code.lower()

    keymaps = archcraftsman.base.execute(
        f'localectl list-keymaps | grep -E "^{lower_country_code}-latin[0-9]+$"',
        check=False,
        force=True,
        capture_output=True,
    )

    if keymaps.returncode == 0:
        return keymaps.output.split("\n")[0]

    if (
        archcraftsman.base.execute(
            f'localectl list-keymaps | grep -E "^{lower_country_code}$"',
            check=False,
            force=True,
            capture_output=True,
        ).returncode
        == 0
    ):
        return lower_country_code

    return DEFAULT_KEYMAP


class PreLaunchInfo:
    """
    The class to contain all pre-launch information.
    """

    def __init__(
        self,
        global_language: archcraftsman.options.Languages = archcraftsman.options.Languages.ENGLISH,
        keymap: str = "en",
        live_console_font: str = "",
        detected_language: str = "en-US",
        detected_country_code: str = "US",
        detected_timezone: str = "Etc/UTC",
    ) -> None:
        self.global_language = global_language
        self.keymap = keymap
        self.live_console_font = live_console_font
        self._detected_language = detected_language
        self._detected_country_code = detected_country_code
        self._detected_timezone = detected_timezone

    def init(self) -> tuple[archcraftsman.options.Languages, str]:
        """
        The method to initialize the pre-launch information with fetched geoip data and return the default language and keymap.
        """
        with urllib.request.urlopen("https://ipapi.co/json") as response:
            geoip_info = json.loads(response.read())
        self._detected_language = str(geoip_info["languages"]).split(",", maxsplit=1)[0]
        self._detected_country_code = geoip_info["country_code"]
        self._detected_timezone = geoip_info["timezone"]

        default_language = parse_detected_language(self._detected_language)
        return default_language, get_default_keymap(
            default_language, self._detected_country_code
        )

    def setup_locale(self):
        """
        The method to set up environment locale.
        """
        archcraftsman.base.print_step(_("Configuring live environment..."), clear=False)
        self.live_console_font = "ter-v16b"
        archcraftsman.base.execute(f'loadkeys "{self.keymap}"')
        archcraftsman.base.execute("setfont ter-v16b")
        dimensions = archcraftsman.base.execute("stty size", capture_output=True).output
        if dimensions:
            split_dimensions = dimensions.split(" ")
            if (
                split_dimensions
                and len(split_dimensions) > 0
                and int(split_dimensions[0]) >= 80
            ):
                self.live_console_font = "ter-v32b"
                archcraftsman.base.execute("setfont ter-v32b")

        formatted_language = self._detected_language.replace("-", "_")
        if (
            archcraftsman.base.execute(
                f'cat /etc/locale.gen | grep "{formatted_language}.UTF-8 UTF-8"',
                check=False,
                force=True,
                capture_output=True,
            ).returncode
            == 0
        ):
            archcraftsman.base.execute(
                f'sed -i "s|#{formatted_language}.UTF-8 UTF-8|{formatted_language}.UTF-8 UTF-8|g" /etc/locale.gen'
            )
            archcraftsman.base.execute("locale-gen")
            os.putenv("LANG", f"{formatted_language}.UTF-8")
            os.putenv("LANGUAGE", f"{formatted_language}.UTF-8")
        else:
            os.putenv("LANG", "en_US.UTF-8")
            os.putenv("LANGUAGE", "en_US.UTF-8")

    def setup_chroot_keyboard(self):
        """
        The method to set the X keyboard of the chrooted system.
        """
        layout: str = self._detected_country_code.lower()
        if (
            archcraftsman.base.execute(
                f'cat /mnt/usr/share/X11/xkb/rules/base.lst | grep -w "{layout}"',
                force=True,
                check=False,
                capture_output=True,
            ).returncode
            != 0
        ):
            return
        content = [
            'Section "InputClass"\n',
            '    Identifier "system-keyboard"\n',
            '    MatchIsKeyboard "on"\n',
            f'    Option "XkbLayout" "{layout}"\n',
            "EndSection\n",
        ]
        archcraftsman.base.execute("mkdir --parents /mnt/etc/X11/xorg.conf.d/")
        try:
            with open(
                "/mnt/etc/X11/xorg.conf.d/00-keyboard.conf", "w", encoding="UTF-8"
            ) as keyboard_config_file:
                keyboard_config_file.writelines(content)
        except FileNotFoundError as exception:
            archcraftsman.base.log(f"Exception: {exception}")

    def country_code(self) -> str:
        """
        The method to get the country code.
        """
        return self._detected_country_code

    def timezone_file(self) -> str:
        """
        The method to get the timezone file path.
        """
        return f"/usr/share/zoneinfo/{self._detected_timezone}"
