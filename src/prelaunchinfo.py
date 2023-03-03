"""
The module of PreLaunchInfo class.
"""
import os

from src.globalargs import GlobalArgs
from src.i18n import I18n
from src.utils import print_step, is_bios, print_error, print_sub_step, prompt_ln, execute, prompt_bool, stdout, log

_ = I18n().gettext


class PreLaunchInfo:
    """
    The class to contain all pre-launch information.
    """
    global_language: str
    keymap: str
    detected_timezone: str
    live_console_font: str

    def prompt(self, detected_language: str, detected_timezone: str):
        """
        The method to get environment configurations from the user.
        :param detected_language:
        :param detected_timezone:
        :return:
        """
        user_answer = False
        while not user_answer:
            print_step(_("Welcome to ArchCraftsman !"))
            if is_bios():
                print_error(
                    _("BIOS detected ! The script will act accordingly. Don't forget to select a DOS label type before "
                      "partitioning."))

            print_step(_("Environment configuration : "), clear=False)

            supported_global_languages = ["FR", "EN"]
            if detected_language == "fr-FR":
                default_language = "FR"
            else:
                default_language = "EN"

            print_step(_("Supported languages : "), clear=False)
            print_sub_step(", ".join(supported_global_languages))
            print('')
            global_language_ok = False
            self.global_language = ""
            self.keymap = ""
            while not global_language_ok:
                self.global_language = prompt_ln(
                    _("Choose your installation's language (%s) : ") % default_language,
                    default=default_language).upper()
                if self.global_language in supported_global_languages:
                    global_language_ok = True
                else:
                    print_error(_("Global language '%s' is not supported.") % self.global_language,
                                do_pause=False)
                    continue

            if detected_language == "fr-FR":
                default_keymap = "fr-latin9"
            else:
                default_keymap = "de-latin1"

            keymap_ok = False
            while not keymap_ok:
                self.keymap = prompt_ln(_("Type your installation's keymap (%s) : ") % default_keymap,
                                        default=default_keymap)
                if execute(f'localectl list-keymaps | grep "^{self.keymap}$" &>/dev/null').returncode == 0:
                    keymap_ok = True
                else:
                    print_error(_("Keymap %s doesn't exist.") % self.keymap)
                    continue

            print_step(_("Summary of choices :"), clear=False)
            print_sub_step(_("Your installation's language : %s") % self.global_language)
            print_sub_step(_("Your installation's keymap : %s") % self.global_language)
            user_answer = prompt_bool(_("Is the informations correct ?"), default=False)
        self.detected_timezone = detected_timezone
        self.setup_locale()

    def setup_locale(self):
        """
        The method to set up environment locale.
        """
        print_step(_("Configuring live environment..."), clear=False)
        self.live_console_font = 'ter-v16b'
        if GlobalArgs().install():
            execute(f'loadkeys "{self.keymap}"')
            execute('setfont ter-v16b')
            dimensions = stdout(execute('stty size', capture_output=True))
            if dimensions:
                split_dimensions = dimensions.split(" ")
                if split_dimensions and len(split_dimensions) > 0 and int(split_dimensions[0]) >= 80:
                    self.live_console_font = 'ter-v32b'
                    execute('setfont ter-v32b')
        if self.global_language == "FR":
            if GlobalArgs().install():
                execute('sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /etc/locale.gen')
                execute('locale-gen')
            os.putenv('LANG', 'fr_FR.UTF-8')
            os.putenv('LANGUAGE', 'fr_FR.UTF-8')
        else:
            os.putenv('LANG', 'en_US.UTF-8')
            os.putenv('LANGUAGE', 'en_US.UTF-8')

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
