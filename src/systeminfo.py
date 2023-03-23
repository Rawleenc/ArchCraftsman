"""
The module of SystemInfo class.
"""

from src.bundles.bundle import Bundle
from src.i18n import I18n

_ = I18n().gettext


class SystemInfo:
    """
    The class to contain all system information.
    """

    hostname: str
    bundles: list[Bundle]
    kernel: Bundle
    desktop: Bundle
    network: Bundle
    bootloader: Bundle
    micro_codes: Bundle
    timezone: str
    user_name: str
    user_full_name: str
    more_pkgs: set[str]
    root_password: str
    user_password: str
