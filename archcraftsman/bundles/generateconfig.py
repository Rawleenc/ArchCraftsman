"""
The yay bundle module
"""

from archcraftsman.base import print_sub_step
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.i18n import I18n

_ = I18n().gettext


class GenerateConfig(Bundle):
    """
    The generate configuration shell bundle.
    """

    def print_resume(self):
        print_sub_step(_("Generate configuration."))
