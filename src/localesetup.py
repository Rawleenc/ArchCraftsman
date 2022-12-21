import os

from src.i18n import I18n
from src.utils import print_step

_ = I18n().gettext

def setup_locale(keymap: str = "de-latin1", global_language: str = "EN") -> str:
    """
    The method to setup environment locale.
    :param keymap:
    :param global_language:
    :return: The configured live system console font (terminus 16 or 32)
    """
    print_step(_("Configuring live environment..."), clear=False)
    os.system(f'loadkeys "{keymap}"')
    font = 'ter-v16b'
    os.system('setfont ter-v16b')
    dimensions = os.popen('stty size').read().split(" ")
    if dimensions and len(dimensions) > 0 and int(dimensions[0]) >= 80:
        font = 'ter-v32b'
        os.system('setfont ter-v32b')
    if global_language == "FR":
        os.system('sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /etc/locale.gen')
        os.system('locale-gen')
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
    os.system("mkdir --parents /mnt/etc/X11/xorg.conf.d/")
    with open("/mnt/etc/X11/xorg.conf.d/00-keyboard.conf", "w", encoding="UTF-8") as keyboard_config_file:
        keyboard_config_file.writelines(content)
