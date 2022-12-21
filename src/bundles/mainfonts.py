from src.bundles.bundle import Bundle
from src.i18n import I18n
from src.utils import print_sub_step

_ = I18n().gettext


def get_main_fonts() -> [str]:
    """
    The method to get the package list of the main fonts group.
    :return:
    """
    return ["gnu-free-fonts", "noto-fonts", "ttf-bitstream-vera", "ttf-dejavu", "ttf-hack", "ttf-droid",
            "ttf-fira-code", "ttf-fira-mono", "ttf-fira-sans", "ttf-font-awesome", "ttf-inconsolata",
            "ttf-input", "ttf-liberation", "ttf-nerd-fonts-symbols-2048-em", "ttf-opensans", "ttf-roboto",
            "ttf-roboto-mono", "ttf-ubuntu-font-family", "ttf-jetbrains-mono", "otf-font-awesome", "noto-fonts-emoji"]


class MainFonts(Bundle):
    """
    The main fonts class.
    """

    def packages(self, system_info: {}) -> [str]:
        return get_main_fonts()

    def print_resume(self):
        print_sub_step(_("Install a set of main fonts."))
