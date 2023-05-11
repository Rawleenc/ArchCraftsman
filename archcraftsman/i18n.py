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
The I18n management singleton module
"""
import gettext

from archcraftsman.options import Languages

_I18N_METHOD = gettext.gettext


def update_method(global_language: str):
    """
    Update the translation method to use according to the global language.
    """

    if global_language != Languages.ENGLISH:
        translation = gettext.translation(
            "archcraftsman",
            localedir="/usr/share/locale",
            languages=[global_language],
        )
        translation.install()
        global _I18N_METHOD
        _I18N_METHOD = translation.gettext


def _t(message) -> str:
    """
    Translate the given text with the translation method.
    """
    return _I18N_METHOD(message)


_ = _t
