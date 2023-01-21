"""
The locale related setup module
"""
import os

from src.i18n import I18n
from src.utils import print_step, execute, log, stdout

_ = I18n().gettext


def setup_locale(keymap: str = "de-latin1", global_language: str = "EN") -> str:
    """
    The method to set up environment locale.
    :param keymap:
    :param global_language:
    :return: The configured live system console font (terminus 16 or 32)
    """
    print_step(_("Configuring live environment..."), clear=False)
    execute(f'loadkeys "{keymap}"')
    font = 'ter-v16b'
    execute('setfont ter-v16b')
    dimensions = stdout(execute('stty size', capture_output=True))
    if dimensions:
        split_dimensions = dimensions.split(" ")
        if split_dimensions and len(split_dimensions) > 0 and int(split_dimensions[0]) >= 80:
            font = 'ter-v32b'
            execute('setfont ter-v32b')
    if global_language == "FR":
        execute('sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /etc/locale.gen')
        execute('locale-gen')
        os.putenv('LANG', 'fr_FR.UTF-8')
        os.putenv('LANGUAGE', 'fr_FR.UTF-8')
    else:
        os.putenv('LANG', 'en_US.UTF-8')
        os.putenv('LANGUAGE', 'en_US.UTF-8')
    return font


def setup_chroot_keyboard(layout: str):
    """
    The method to set the X keyboard of the chrooted system.
    :param layout:
    """
    content = [
        "Section \"InputClass\"\n",
        "    Identifier \"system-keyboard\"\n",
        "    MatchIsKeyboard \"on\"\n",
        f"    Option \"XkbLayout\" \"{layout}\"\n",
        "EndSection\n"
    ]
    execute("mkdir --parents /mnt/etc/X11/xorg.conf.d/")
    try:
        with open("/mnt/etc/X11/xorg.conf.d/00-keyboard.conf", "w", encoding="UTF-8") as keyboard_config_file:
            keyboard_config_file.writelines(content)
    except FileNotFoundError as exception:
        log(f"Exception: {exception}")
