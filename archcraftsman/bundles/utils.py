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
The bundles related utility methods and tools module
"""
import importlib
from importlib.resources import files
from typing import Optional, TypeVar

from archcraftsman.bundles.bundle import Bundle
from archcraftsman.options import OptionEnum
from archcraftsman.utils import prompt_option


def get_all_bundle_types() -> list[type[Bundle]]:
    """
    A function to get all available bundles.
    """
    for name in list(
        f'archcraftsman.bundles.{resource.name.replace(".py", "")}'
        for resource in files("archcraftsman.bundles").iterdir()
        if resource.is_file()
        and resource.name.endswith(".py")
        and resource.name != "__init__.py"
    ):
        importlib.import_module(name)
    return Bundle.__subclasses__()


_BUNDLES_MAP: dict[str, type[Bundle]] = {
    bundle().name: bundle for bundle in get_all_bundle_types()
}


def get_bundle_type_by_name(name: str) -> type[Bundle]:
    """
    A function to get the bundle type by its name.
    """
    return _BUNDLES_MAP[name] if name in _BUNDLES_MAP else Bundle


def list_generic_bundles() -> list[str]:
    """
    List all available generic bundles.
    """
    return list(
        resource.name.replace(".toml", "")
        for resource in files("archcraftsman.bundles.configs").iterdir()
        if resource.is_file() and resource.name.endswith(".toml")
    )


def process_bundle(name: OptionEnum) -> Bundle:
    """
    Process a bundle name into a Bundle object.
    """
    return get_bundle_type_by_name(name.value)()


T = TypeVar("T", bound=OptionEnum)


def prompt_bundle(
    message: str,
    error_msg: str,
    options: type[T],
    supported_msg: Optional[str],
    default: Optional[T],
    *ignores: T,
    new_line_prompt: bool = True,
) -> Bundle:
    """
    A method to prompt for a bundle.
    """
    option = prompt_option(
        message,
        error_msg,
        options,
        supported_msg,
        default,
        *ignores,
        new_line_prompt=new_line_prompt,
    )
    if not option:
        raise ValueError("No bundle selected")
    bundle = process_bundle(option)
    bundle.prompt_extra()
    return bundle
