"""
The environment setup module
"""

from src.i18n import I18n
from src.utils import print_step, is_bios, print_error, print_sub_step, prompt_ln, prompt_bool, execute

_ = I18n().gettext


def setup_environment(detected_language: str) -> dict[str, any]:
    """
    The method to get environment configurations from the user.
    :param detected_language:
    :return:
    """
    pre_launch_info = {"global_language": None, "keymap": None}
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
        pre_launch_info["global_language"] = None
        pre_launch_info["keymap"] = None
        while not global_language_ok:
            pre_launch_info["global_language"] = prompt_ln(
                _("Choose your installation's language (%s) : ") % default_language,
                default=default_language).upper()
            if pre_launch_info["global_language"] in supported_global_languages:
                global_language_ok = True
            else:
                print_error(_("Global language '%s' is not supported.") % pre_launch_info["global_language"],
                            do_pause=False)
                continue

        if detected_language == "fr-FR":
            default_keymap = "fr-latin9"
        else:
            default_keymap = "de-latin1"

        keymap_ok = False
        while not keymap_ok:
            pre_launch_info["keymap"] = prompt_ln(_("Type your installation's keymap (%s) : ") % default_keymap,
                                                  default=default_keymap)
            if execute(f'localectl list-keymaps | grep "^{pre_launch_info["keymap"]}$" &>/dev/null').returncode == 0:
                keymap_ok = True
            else:
                print_error(_("Keymap %s doesn't exist.") % pre_launch_info["keymap"])
                continue

        print_step(_("Summary of choices :"), clear=False)
        print_sub_step(_("Your installation's language : %s") % pre_launch_info["global_language"])
        print_sub_step(_("Your installation's keymap : %s") % pre_launch_info["keymap"])
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
    return pre_launch_info
