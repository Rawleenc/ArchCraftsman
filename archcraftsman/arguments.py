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
import argparse
import typing

_ARGS = argparse.Namespace()


def init(args: typing.Optional[argparse.Namespace] = None) -> None:
    """
    Initialize the global arguments.
    """
    if args:
        global _ARGS
        _ARGS = args
    if not hasattr(_ARGS, "install"):
        _ARGS.install = False
    if not hasattr(_ARGS, "shell"):
        _ARGS.shell = False
    if not hasattr(_ARGS, "config"):
        _ARGS.config = ""
    if not hasattr(_ARGS, "test"):
        _ARGS.test = False


init()


def is_call_ok() -> bool:
    """
    Check if the installer is called correctly.
    """
    return _ARGS and (install() or shell())


def install() -> bool:
    """
    Check if the installer is in installation mode.
    """
    return _ARGS and _ARGS.install


def shell() -> bool:
    """
    Check if the installer is in shell mode.
    """
    return _ARGS and _ARGS.shell


def config() -> str:
    """
    Check if the installer is in shell mode.
    """
    return _ARGS and _ARGS.config


def test() -> bool:
    """
    Check if the installer is in fake test mode.
    """
    return _ARGS and _ARGS.test
