""" An Arch Linux install script. """
import gettext
import glob
import json
import os
import re
import readline
import string
import getpass
import urllib.request

RED = "\033[0;31m"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
ORANGE = "\033[0;33m"
NOCOLOR = "\033[0m"


def complete(text, state):
    """
    A file path completer.
    :param text:
    :param state:
    :return:
    """
    return (glob.glob(text + '*') + [None])[state]


readline.set_completer_delims(' \t\n;')
readline.parse_and_bind("tab: complete")
readline.set_completer(complete)


def print_error(message: string):
    """
    A method to print an error.
    :param message:
    :return:
    """
    print(f'\n{RED}  /!\\ {message}{NOCOLOR}')
    pause()


def print_step(message: string, clear: bool = True):
    """
    A method to print a step message.
    :param message:
    :param clear:
    """
    if clear:
        os.system('clear')
    print(f'\n{GREEN}{message}{NOCOLOR}')


def print_sub_step(message: string):
    """
    A method to print a sub step message.
    :param message:
    """
    print(f'{CYAN}  * {message}{NOCOLOR}')


def prompt(message: string, default: string = None) -> string:
    """
    A method to prompt for a user input.
    :param message:
    :param default:
    :return:
    """
    user_input = input(f'{ORANGE}{message}{NOCOLOR}')
    if user_input == "" and default is not None:
        user_input = default
    return user_input


def prompt_ln(message: string, default: string = None) -> string:
    """
    A method to prompt for a user input with a new line for the user input.
    :param message:
    :param default:
    :return:
    """
    return prompt(f'{message}\n', default)


def prompt_bool(message: string, default: bool = True) -> bool:
    """
    A method to prompt for a boolean choice.
    :param message:
    :param default:
    :return:
    """
    if not default:
        return input(f'{ORANGE}{message}{NOCOLOR}').upper() in {"Y", "O"}
    return input(f'{ORANGE}{message}{NOCOLOR}').upper() == "N"


def prompt_passwd(message: string):
    """
    A method to prompt for a password without displaying an echo.
    :param message:
    :return:
    """
    return getpass.getpass(prompt=f'{ORANGE}{message}{NOCOLOR}')


def pause(start_newline: bool = False, end_newline: bool = False):
    """
    A method to insert a one key press pause.
    :param start_newline:
    :param end_newline:
    """
    message = _("Press any key to continue...")
    if start_newline:
        print("")
    print(f'{ORANGE}{message}{NOCOLOR}')
    if end_newline:
        print("")
    os.system('read -n 1 -sr')


def locale_setup(keymap: string = "de-latin1", global_language: string = "EN"):
    """
    The method to setup environment locale.
    :param keymap:
    :param global_language:
    """
    print_step(_("Configuring live environment..."), clear=False)
    os.system(f'loadkeys "{keymap}"')
    os.system('setfont eurlatgr')
    if global_language == "FR":
        os.system('sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /etc/locale.gen')
        os.system('locale-gen')
        os.putenv('LANG', 'fr_FR.UTF-8')
        os.putenv('LANGUAGE', 'fr_FR.UTF-8')
    else:
        os.putenv('LANG', 'en_US.UTF-8')
        os.putenv('LANGUAGE', 'en_US.UTF-8')


def setup_chroot_keyboard(layout: string):
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
    with open("/mnt/etc/X11/xorg.conf.d/00-keyboard.conf", "w", encoding="UTF-8") as keyboard_config_file:
        keyboard_config_file.writelines(content)


def ask_swapfile_size() -> string:
    """
    The method to ask the user for the swapfile size.
    :return:
    """
    swapfile_ok = False
    swapfile_size = ""
    swapfile_size_pattern = re.compile("^([0-9]*[.,][0-9][0-9]*|[0-9][0-9]*)([GMk])$")
    while not swapfile_ok:
        swapfile_size = prompt(_("Swapfile size ? (Example: 8G, leave empty if none) : "))
        if swapfile_size_pattern.match(swapfile_size):
            swapfile_ok = True
        else:
            print_error("Invalid swapfile size.")
    return swapfile_size


def manual_partitioning(bios: string):
    """
    The method to proceed to the manual partitioning.
    :param bios:
    :return:
    """
    partitions = set()
    part_type = {}
    part_mount_point = {}
    part_format = {}
    root_partition = None
    swap_partition = None
    swapfile_size = None
    main_disk = None
    user_answer = False
    partitioned_disks = set()
    while not user_answer:
        print_step(_("Manual partitioning :"))
        print_sub_step(_("Partitioned drives so far : %s") % " ".join(partitioned_disks))
        os.system('fdisk -l')
        target_disk = prompt(
            "Which drive do you want to partition ? (partition_type the entire name, for example '/dev/sda') : ")
        if not os.path.exists(target_disk):
            print_error(_("The chosen target drive doesn't exist."))
            continue
        partitioned_disks.add(target_disk)
        os.system(f'cfdisk "{target_disk}"')
        print_step(_("Manual partitioning :"))
        print_sub_step(_("Partitioned drives so far : %s") % " ".join(partitioned_disks))
        os.system('fdisk -l')
        other_drive = prompt_bool(_("Do you want to partition an other drive ? (y/N) : "), default=False)
        if other_drive:
            continue
        for disk in partitioned_disks:
            detected_partitions = os.popen(
                f'lsblk -nl "{disk}" -o PATH,PARTTYPENAME | grep -iE "linux|efi|swap" | awk \'{{print $1}}\'').read()
            for partition in detected_partitions.splitlines():
                partitions.add(partition)
        print_step(_("Detected target drive partitions : %s") % " ".join(partitions))
        for partition in partitions:
            print_sub_step(_("Partition : %s") % os.popen(f'lsblk -nl "{partition}" -o PATH,SIZE,PARTTYPENAME').read())
            if bios:
                partition_type = prompt(
                    _("What is the role of this partition ? (1: Root, 2: Home, 3: Swap, 4: Not used, other: Other) : "))
            else:
                partition_type = prompt(
                    _("What is the role of this partition ? (0: EFI, 1: Root, 2: Home, 3: Swap, 4: Not used, other: Other) : "))
            if not bios and partition_type == "0":
                part_type[partition] = "EFI"
                part_mount_point[partition] = "/boot/efi"
                part_format[partition] = prompt_bool(_("Format the EFI partition ? (Y/n) : "))
            elif partition_type == "1":
                part_type[partition] = "ROOT"
                part_mount_point[partition] = "/"
                root_partition = partition
            elif partition_type == "2":
                part_type[partition] = "HOME"
                part_mount_point[partition] = "/home"
                part_format[partition] = prompt_bool(_("Format the Home partition ? (Y/n) : "))
            elif partition_type == "3":
                part_type[partition] = "SWAP"
                swap_partition = partition
            elif partition_type == "4":
                continue
            else:
                part_type[partition] = "OTHER"
                part_mount_point[partition] = prompt(_("What is the mounting point of this partition ? : "))
                part_format[partition] = prompt_bool(_("Format the %s partition ? (Y/n) : ") % partition)
                if "/boot" in part_mount_point[partition]:
                    main_disk = os.popen(f'lsblk -ndo PKNAME {partition}').read()
        if "SWAP" not in part_type.values():
            swapfile_size = ask_swapfile_size()
        if not bios and "EFI" not in part_type.values():
            print_error(_("The EFI partition is required for system installation."))
            partitions.clear()
            partitioned_disks.clear()
            continue
        if "ROOT" not in part_type.values():
            print_error(_("The Root partition is required for system installation."))
            partitions.clear()
            partitioned_disks.clear()
            continue
        print_step(_("Summary of choices :"))
        for partition in partitions:
            if part_format.get(partition):
                formatting = _("yes")
            else:
                formatting = _("no")
            if part_type[partition] == "EFI":
                print_sub_step(_("EFI partition : %s (mounting point : %s, format %s)")
                               % (partition, part_mount_point[partition], formatting))
            if part_type[partition] == "ROOT":
                print_sub_step(_("ROOT partition : %s (mounting point : %s)")
                               % (partition, part_mount_point[partition]))
            if part_type[partition] == "HOME":
                print_sub_step(_("Home partition : %s (mounting point : %s, format %s)")
                               % (partition, part_mount_point[partition], formatting))
            if part_type[partition] == "SWAP":
                print_sub_step(_("Swap partition : %s") % partition)
            if part_type[partition] == "OTHER":
                print_sub_step(_("Other partition : %s (mounting point : %s, format %s)")
                               % (partition, part_mount_point[partition], formatting))
        if "SWAP" not in part_type.values() and swapfile_size is not None:
            print_sub_step(_("Swapfile size : %s") % swapfile_size)
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
        if not user_answer:
            partitions.clear()
            partitioned_disks.clear()
    return partitions, part_type, part_mount_point, part_format, root_partition, swap_partition, swapfile_size, main_disk


def build_partition_name(disk: string, index: string):
    """
    A method to build a partition name with a disk and an index.
    :param disk:
    :param index:
    :return:
    """
    return (f'{disk}{index}', f'{disk}p{index}')["nvme" in disk]


def auto_partitioning(bios: string):
    """
    The method to proceed to the automatic partitioning.
    :param bios:
    :return:
    """
    partitions = set()
    part_type = {}
    part_mount_point = {}
    part_format = {}
    root_partition = None
    swap_partition = None
    swapfile_size = None
    main_disk = None
    user_answer = False
    while not user_answer:
        print_step(_("Automatic partitioning :"))
        os.system("fdisk -l")
        target_disk = prompt(
            _("On which drive should Archlinux be installed ? (type the entire name, for example '/dev/sda') : "))
        if target_disk == "":
            print_error(_("You need to choose a target drive."))
            continue
        if not os.path.exists(target_disk):
            print_error(_("You need to choose a target drive."))
            continue
        swap_type = prompt(_("What type of Swap do you want ? (1: Partition, other: File) : "))
        want_home = prompt_bool(_("Do you want a separated Home ? (y/N) : "), default=False)
        main_disk = target_disk
        target_disk_size = int(os.popen(f'lsblk -b --output SIZE -n -d "{target_disk}"').read())
        root_size = os.popen(f'printf "{int(target_disk_size / 4)}" | numfmt --to=iec').read()
        swap_size = os.popen(f'printf "{int(target_disk_size / 32)}" | numfmt --to=iec').read()
        if swap_type != "1":
            swapfile_size = swap_size
        auto_part_str = ""
        index = 0
        if bios:
            # DOS LABEL
            auto_part_str += "o\n"  # Create a new empty DOS partition table
            # BOOT
            auto_part_str += "n\n"  # Add a new partition
            auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += "+1G\n"  # Last sector (Accept default: varies)
            auto_part_str += "a\n"  # Toggle bootable flag
            index += 1
            partition = build_partition_name(target_disk, index)
            part_type[partition] = "OTHER"
            part_mount_point[partition] = "/boot"
            part_format[partition] = True
            partitions.add(partition)
        else:
            # GPT LABEL
            auto_part_str += "g\n"  # Create a new empty GPT partition table
            # EFI
            auto_part_str += "n\n"  # Add a new partition
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += "+512M\n"  # Last sector (Accept default: varies)
            auto_part_str += "t\n"  # Change partition type
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += "1\n"  # Type EFI System
            index += 1
            partition = build_partition_name(target_disk, index)
            part_type[partition] = "EFI"
            part_mount_point[partition] = "/boot/efi"
            part_format[partition] = True
            partitions.add(partition)
        if swap_type == "1":
            # SWAP
            auto_part_str += "n\n"  # Add a new partition
            if bios:
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += f'+{swap_size}\n'  # Last sector (Accept default: varies)
            auto_part_str += "t\n"  # Change partition type
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            if bios:
                auto_part_str += "82\n"  # Type Linux Swap
            else:
                auto_part_str += "19\n"  # Type Linux Swap
            index += 1
            partition = build_partition_name(target_disk, index)
            part_type[partition] = "SWAP"
            swap_partition = partition
            partitions.add(partition)
        if want_home:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if bios:
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += f'+{root_size}\n'  # Last sector (Accept default: varies)
            index += 1
            partition = build_partition_name(target_disk, index)
            part_type[partition] = "ROOT"
            part_mount_point[partition] = "/"
            root_partition = partition
            partitions.add(partition)
            # HOME
            auto_part_str += "n\n"  # Add a new partition
            if bios:
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            index += 1
            partition = build_partition_name(target_disk, index)
            part_type[partition] = "HOME"
            part_mount_point[partition] = "/home"
            part_format[partition] = True
            partitions.add(partition)
        else:
            # ROOT
            auto_part_str += "n\n"  # Add a new partition
            if bios:
                auto_part_str += "p\n"  # Partition primary (Accept default: primary)
            auto_part_str += " \n"  # Partition number (Accept default: auto)
            auto_part_str += " \n"  # First sector (Accept default: 1)
            auto_part_str += " \n"  # Last sector (Accept default: varies)
            index += 1
            partition = build_partition_name(target_disk, index)
            part_type[partition] = "ROOT"
            part_mount_point[partition] = "/"
            root_partition = partition
            partitions.add(partition)
        # WRITE
        auto_part_str += "w\n"
        os.system(f'echo -e "{auto_part_str}" | fdisk "{target_disk}" &>/dev/null')
        print_step(_("Summary of choices :"), clear=False)
        for partition in partitions:
            if part_format.get(partition):
                formatting = _("yes")
            else:
                formatting = _("no")
            if part_type[partition] == "EFI":
                print_sub_step(_("EFI partition : %s (mounting point : %s, format %s)")
                               % (partition, part_mount_point[partition], formatting))
            if part_type[partition] == "ROOT":
                print_sub_step(_("ROOT partition : %s (mounting point : %s)")
                               % (partition, part_mount_point[partition]))
            if part_type[partition] == "HOME":
                print_sub_step(_("Home partition : %s (mounting point : %s, format %s)")
                               % (partition, part_mount_point[partition], formatting))
            if part_type[partition] == "SWAP":
                print_sub_step(_("Swap partition : %s") % partition)
            if part_type[partition] == "OTHER":
                print_sub_step(_("Other partition : %s (mounting point : %s, format %s)")
                               % (partition, part_mount_point[partition], formatting))
        if "SWAP" not in part_type.values() and swap_size is not None:
            print_sub_step(_("Swapfile size : %s") % swap_size)
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
        if not user_answer:
            partitions.clear()
    return partitions, part_type, part_mount_point, part_format, root_partition, swap_partition, swapfile_size, main_disk


def environment_config(detected_language: string):
    """
    The method to get environment configurations from the user.
    :param detected_language:
    :return:
    """
    global_language = None
    keymap = None
    bios = None
    user_answer = False
    while not user_answer:
        print_step(_("Welcome to the archlinux-install script !"))
        bios = not os.path.exists("/sys/firmware/efi")
        if bios:
            print_error(
                _("BIOS detected ! The script will act accordingly. Don't forget to select a DOS label type before partitioning."))

        print_step(_("Environment configuration : "), clear=False)

        supported_global_languages = ["FR", "EN"]
        if detected_language == "fr-FR":
            default_language = "FR"
        else:
            default_language = "EN"
        global_language_ok = False
        global_language = None
        keymap = None
        while not global_language_ok:
            global_language = prompt_ln(
                _("Choose your installation's language (%s, type 'h' or 'help' to list supported languages) : ") % default_language,
                default=default_language).upper()
            if global_language in {"H", "HELP"}:
                print_step(_("Supported languages : "), clear=False)
                for language in supported_global_languages:
                    print_sub_step(language)
                pause(start_newline=True)
                continue
            if global_language in supported_global_languages:
                global_language_ok = True
            else:
                print_error(_("Global language %s is not supported.") % global_language)
                continue

        if detected_language == "fr-FR":
            default_keymap = "fr-latin9"
        else:
            default_keymap = "de-latin1"

        keymap_ok = False
        while not keymap_ok:
            keymap = prompt_ln(_("Type your installation's keymap (%s) : ") % default_keymap, default=default_keymap)
            if os.system(f'localectl list-keymaps | grep "^{keymap}$" &>/dev/null') == 0:
                keymap_ok = True
            else:
                print_error(_("Keymap %s doesn't exist.") % keymap)
                continue

        print_step(_("Summary of choices :"), clear=False)
        print_sub_step(_("Your installation's language : %s") % global_language)
        print_sub_step(_("Your installation's keymap : %s") % keymap)
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
    return bios, global_language, keymap


def ask_password(username: string = "root"):
    """
    A method to ask a password to the user.
    :param username:
    :return:
    """
    password_confirm = None
    password = ""
    while password != password_confirm:
        print_sub_step(_("%s password configuration : ") % username)
        password = prompt_passwd(_("Enter the %s password : ") % username)
        password_confirm = prompt_passwd(_("Re-enter the %s password to confirm : ") % username)
        if password != password_confirm:
            print_error(_("Passwords entered don't match."))
    return password


def system_config(detected_timezone):
    """
    The method to get system configurations from the user.
    :param detected_timezone:
    :return:
    """
    system_info = {}
    user_answer = False
    while not user_answer:
        print_step(_("System configuration : "))
        system_info["hostname"] = prompt(_("What will be your hostname (archlinux) : "), default="archlinux")
        system_info["lts_kernel"] = prompt_bool(_("Install LTS Linux kernel ? (y/N) : "), default=False)
        system_info["nvidia_driver"] = prompt_bool(_("Install proprietary Nvidia driver ? (y/N) : "), default=False)
        system_info["terminus_font"] = prompt_bool(_("Install terminus console font ? (y/N) : "), default=False)
        system_info["desktop"] = prompt(
            _("Install a desktop environment ? (1: Gnome, 2: KDE Plasma, 3: XFCE, other: None) : "))
        system_info["plasma_wayland"] = False
        if system_info["desktop"] == "2":
            system_info["plasma_wayland"] = prompt_bool(_("Install Wayland support for the plasma session ? (y/N) : "),
                                                        default=False)
        system_info["cups"] = prompt_bool(_("Install Cups ? (y/N) : "), default=False)
        system_info["grml_zsh"] = prompt_bool(_("Install ZSH with GRML configuration ? (y/N) : "), default=False)
        system_info["main_fonts"] = prompt_bool(_("Install a set of main fonts ? (y/N) : "), default=False)
        system_info["main_file_systems"] = prompt_bool(_("Install main file systems support ? (y/N) : "), default=False)
        default_timezone_file = f'/usr/share/zoneinfo/{detected_timezone}'
        system_info["timezone"] = prompt_ln(_("Your timezone (%s) : ") % default_timezone_file,
                                            default=default_timezone_file)
        system_info["user_name"] = prompt_ln(_("Would you like to add a user? (type username, leave blank if none) : "))
        system_info["user_full_name"] = ""
        if system_info["user_name"] != "":
            system_info["user_full_name"] = prompt_ln(
                _("What is the %s's full name (type the entire full name, leave blank if none) : ") % system_info[
                    "user_name"])

        pkgs_select_ok = False
        system_info["more_pkgs"] = []
        while not pkgs_select_ok:
            more_pkgs_str = prompt_ln(
                _("Install more packages ? (type extra packages full names, example : 'htop neofetch', leave blank if none) : "))
            pkgs_select_ok = True
            if more_pkgs_str != "":
                system_info["more_pkgs"] = more_pkgs_str.split(" ")
                for pkg in system_info["more_pkgs"]:
                    if os.system(f'pacman -Ss ^"{pkg}"$ &>/dev/null') != 0:
                        pkgs_select_ok = False
                        print_error(_("Package %s doesn't exist.") % pkg)
                        break

        system_info["root_password"] = ask_password()
        if system_info["user_name"] != "":
            system_info["user_password"] = ask_password(system_info["user_name"])

        if system_info["desktop"] == "1":
            system_info["desktop"] = "gnome"
        elif system_info["desktop"] == "2":
            system_info["desktop"] = "plasma"
        elif system_info["desktop"] == "3":
            system_info["desktop"] = "xfce"
        else:
            system_info["desktop"] = _("none")

        system_info["microcodes"] = re.sub(
            '\\s+', '', os.popen('grep </proc/cpuinfo "vendor" | uniq').read()).split(":")[1]

        print_step(_("Summary of choices :"))
        print_sub_step(_("Your hostname : %s") % system_info["hostname"])
        if system_info["microcodes"] in {"GenuineIntel", "AuthenticAMD"}:
            print_sub_step(_("Microcodes to install : %s") % system_info["microcodes"])
        if system_info["lts_kernel"]:
            print_sub_step(_("Install LTS Linux kernel."))
        if system_info["nvidia_driver"]:
            print_sub_step(_("Install proprietary Nvidia driver."))
        if system_info["terminus_font"]:
            print_sub_step(_("Install terminus console font."))
        print_sub_step(_("Desktop environment : %s") % system_info["desktop"])
        if system_info["desktop"] == "plasma" and system_info["plasma_wayland"]:
            print_sub_step(_("Install Wayland support for the plasma session."))
        if system_info["cups"]:
            print_sub_step(_("Install Cups."))
        if system_info["grml_zsh"]:
            print_sub_step(_("Install ZSH with GRML configuration."))
        if system_info["main_fonts"]:
            print_sub_step(_("Install a set of main fonts."))
        if system_info["main_file_systems"]:
            print_sub_step(_("Install main file systems support."))
        print_sub_step(_("Your timezone : %s") % system_info["timezone"])
        if system_info["user_name"] != "":
            print_sub_step(_("Additional user name : %s") % system_info["user_name"])
            if system_info["user_full_name"] != "":
                print_sub_step(_("User's full name : %s") % system_info["user_full_name"])
        if system_info["more_pkgs"]:
            print_sub_step(_("More packages to install : %s") % " ".join(system_info["more_pkgs"]))
        user_answer = prompt_bool(_("Is the informations correct ? (y/N) : "), default=False)
    return system_info


def umount_partitions(swap_partition, swapfile_size):
    """
    A method to unmount all mounted partitions.
    :param swap_partition:
    :param swapfile_size:
    """
    print_step(_("Unmounting partitions..."), clear=False)
    if swap_partition is None and swapfile_size not in (None, ""):
        os.system('swapoff /mnt/swapfile')
    if swap_partition is not None:
        os.system(f'swapoff "${swap_partition}"')
    os.system('umount -R /mnt')


def main(bios, detected_country_code, detected_timezone, global_language, keymap):
    """ The main method. """
    system_info = system_config(detected_timezone)

    print_step(_("Partitioning :"))
    want_auto_part = prompt_bool(_("Do you want an automatic partitioning ? (y/N) : "), default=False)
    if want_auto_part:
        partitions, part_type, part_mount_point, part_format, root_partition, swap_partition, swapfile_size, main_disk = auto_partitioning(
            bios)
    else:
        partitions, part_type, part_mount_point, part_format, root_partition, swap_partition, swapfile_size, main_disk = manual_partitioning(
            bios)

    print_step(_("Formatting and mounting partitions..."), clear=False)

    os.system(f'mkfs.ext4 "{root_partition}"')
    os.system(f'mkdir -p "/mnt{part_mount_point[root_partition]}"')
    os.system(f'mount "{root_partition}" "/mnt{part_mount_point[root_partition]}"')

    for partition in partitions:
        if not bios and part_type[partition] == "EFI":
            if part_format.get(partition):
                os.system(f'mkfs.vfat "{partition}"')
            os.system(f'mkdir -p "/mnt{part_mount_point[partition]}"')
            os.system(f'mount "{partition}" "/mnt{part_mount_point[partition]}"')
        elif part_type[partition] == "HOME":
            if part_format.get(partition):
                os.system(f'mkfs.ext4 "{partition}"')
            os.system(f'mkdir -p "/mnt{part_mount_point[partition]}"')
            os.system(f'mount "{partition}" "/mnt{part_mount_point[partition]}"')
        elif part_type[partition] == "SWAP":
            os.system(f'mkswap "{partition}"')
            os.system(f'swapon "{partition}"')
        elif part_type[partition] == "OTHER":
            if part_format.get(partition):
                os.system(f'mkfs.ext4 "{partition}"')
            os.system(f'mkdir -p "/mnt{part_mount_point[partition]}"')
            os.system(f'mount "{partition}" "/mnt{part_mount_point[partition]}"')

    if "SWAP" not in part_type.values() and swapfile_size is not None:
        print_step(_("Creation and activation of the swapfile..."), clear=False)
        os.system(f'fallocate -l "{swapfile_size}" /mnt/swapfile')
        os.system('chmod 600 /mnt/swapfile')
        os.system('mkswap /mnt/swapfile')
        os.system('swapon /mnt/swapfile')

    print_step(_("Updating mirrors..."), clear=False)
    os.system(
        f'reflector --save /etc/pacman.d/mirrorlist --protocol https --age 12 --country "{detected_country_code}" --score 5 --sort rate')

    print_step(_("Installation of the base..."), clear=False)
    pkgs = ["base", "base-devel", "linux-firmware", "man-db", "man-pages", "texinfo", "nano", "vim", "git", "curl",
            "grub", "os-prober", "efibootmgr", "networkmanager", "xdg-user-dirs", "reflector", "numlockx", "ntp"]
    if system_info["microcodes"] == "GenuineIntel":
        pkgs.append("intel-ucode")
    if system_info["microcodes"] == "AuthenticAMD":
        pkgs.append("amd-ucode")
    if system_info["lts_kernel"]:
        pkgs.append("linux-lts")
    else:
        pkgs.append("linux")
    if system_info["nvidia_driver"] and system_info["lts_kernel"]:
        pkgs.append("nvidia-lts")
    elif system_info["nvidia_driver"] and not system_info["lts_kernel"]:
        pkgs.append("nvidia")
    if system_info["terminus_font"]:
        pkgs.append("terminus-font")
    if system_info["desktop"] == "gnome":
        pkgs.extend(["gnome", "gnome-extra", "alsa-utils", "pulseaudio", "pulseaudio-alsa"])
    elif system_info["desktop"] == "plasma":
        pkgs.extend(["plasma", "kde-applications", "xorg-server", "alsa-utils", "pulseaudio", "pulseaudio-alsa"])
        if system_info["plasma_wayland"]:
            pkgs.append("plasma-wayland-session")
            if system_info["nvidia_driver"]:
                pkgs.append("egl-wayland")
    elif system_info["desktop"] == "xfce":
        pkgs.extend(
            ["xfce4", "xfce4-goodies", "lightdm", "lightdm-gtk-greeter", "lightdm-gtk-greeter-settings", "xorg-server",
             "alsa-utils", "pulseaudio", "pulseaudio-alsa", "pavucontrol"])
    if system_info["cups"]:
        pkgs.extend(
            ["cups", "cups-pdf", "avahi", "samba", "foomatic-db-engine", "foomatic-db", "foomatic-db-ppds",
             "foomatic-db-nonfree-ppds", "foomatic-db-gutenprint-ppds", "gutenprint", "ghostscript"])
    if system_info["grml_zsh"]:
        pkgs.extend(["zsh", "zsh-completions", "grml-zsh-config"])
    if system_info["main_fonts"]:
        pkgs.extend(["gnu-free-fonts", "noto-fonts", "ttf-bitstream-vera", "ttf-dejavu", "ttf-hack", "ttf-droid",
                     "ttf-fira-code", "ttf-fira-mono", "ttf-fira-sans", "ttf-font-awesome", "ttf-inconsolata",
                     "ttf-input", "ttf-liberation", "ttf-nerd-fonts-symbols", "ttf-opensans", "ttf-roboto",
                     "ttf-roboto-mono", "ttf-ubuntu-font-family", "ttf-jetbrains-mono"])
    if system_info["main_file_systems"]:
        pkgs.extend(
            ["btrfs-progs", "dosfstools", "exfatprogs", "exfat-utils", "f2fs-tools", "e2fsprogs", "jfsutils",
             "nilfs-utils", "ntfs-3g", "reiserfsprogs", "udftools", "xfsprogs"])
    if len(system_info["more_pkgs"]) > 0:
        pkgs.extend(system_info["more_pkgs"])
    os.system(f'pacstrap /mnt {" ".join(pkgs)}')

    print_step(_("System configuration..."), clear=False)
    os.system('genfstab -U /mnt >>/mnt/etc/fstab')
    os.system('sed -i "s|#en_US.UTF-8 UTF-8|en_US.UTF-8 UTF-8|g" /mnt/etc/locale.gen')
    os.system('sed -i "s|#en_US ISO-8859-1|en_US ISO-8859-1|g" /mnt/etc/locale.gen')
    if global_language == "FR":
        os.system('sed -i "s|#fr_FR.UTF-8 UTF-8|fr_FR.UTF-8 UTF-8|g" /mnt/etc/locale.gen')
        os.system('sed -i "s|#fr_FR ISO-8859-1|fr_FR ISO-8859-1|g" /mnt/etc/locale.gen')
        os.system('echo "LANG=fr_FR.UTF-8" >/mnt/etc/locale.conf')
    else:
        os.system('echo "LANG=en_US.UTF-8" >/mnt/etc/locale.conf')
    os.system(f'echo "KEYMAP={keymap}" >/mnt/etc/vconsole.conf')
    if system_info["terminus_font"]:
        os.system('echo "FONT=ter-v16b" >>/mnt/etc/vconsole.conf')
    else:
        os.system('echo "FONT=eurlatgr" >>/mnt/etc/vconsole.conf')
    os.system('sed -i "s|#Color|Color|g" /mnt/etc/pacman.conf')
    os.system(f'echo "{system_info["hostname"]}" >/mnt/etc/hostname')
    os.system(f'''
        {{
            echo "127.0.0.1 localhost"
            echo "::1 localhost"
            echo "127.0.1.1 {system_info["hostname"]}.localdomain {system_info["hostname"]}"
        }} >>/mnt/etc/hostname
    ''')

    print_step(_("Locales configuration..."), clear=False)
    os.system(f'arch-chroot /mnt bash -c "ln -sf {system_info["timezone"]} /etc/localtime"')
    os.system('arch-chroot /mnt bash -c "locale-gen"')
    print_step(_("Network configuration..."), clear=False)
    os.system('arch-chroot /mnt bash -c "systemctl enable NetworkManager"')
    os.system('arch-chroot /mnt bash -c "systemctl enable ntpd"')
    print_step(_("Installation and configuration of the grub..."), clear=False)
    if bios:
        os.system(f'arch-chroot /mnt bash -c "grub-install --target=i386-pc {main_disk}"')
    else:
        os.system(
            'arch-chroot /mnt bash -c "grub-install --target=x86_64-efi --efi-directory=/boot/efi --bootloader-id=\'Arch Linux\'"')
    os.system('arch-chroot /mnt bash -c "grub-mkconfig -o /boot/grub/grub.cfg"')

    print_step(_("Extra packages configuration if needed..."), clear=False)
    if system_info["desktop"] == "gnome":
        os.system('arch-chroot /mnt bash -c "systemctl enable gdm"')
    if system_info["desktop"] == "plasma":
        os.system('arch-chroot /mnt bash -c "systemctl enable sddm"')
    if system_info["desktop"] == "xfce":
        os.system('arch-chroot /mnt bash -c "systemctl enable lightdm"')
    if system_info["desktop"] in {"gnome", "plasma", "xfce"}:
        os.system('arch-chroot /mnt bash -c "amixer sset Master unmute"')
        if "fr" in keymap:
            setup_chroot_keyboard("fr")
    if system_info["cups"]:
        os.system('arch-chroot /mnt bash -c "systemctl enable avahi-daemon"')
        os.system('arch-chroot /mnt bash -c "systemctl enable cups"')
        os.system('arch-chroot /mnt bash -c "systemctl enable cups-browsed"')

    print_step(_("Users configuration..."), clear=False)
    print_sub_step(_("root account configuration..."))
    if system_info["grml_zsh"]:
        os.system('arch-chroot /mnt bash -c "chsh --shell /bin/zsh"')
    if system_info["root_password"] != "":
        os.system(f'arch-chroot /mnt bash -c "echo \'root:{system_info["root_password"]}\' | chpasswd"')
    if system_info["user_name"] != "":
        print_sub_step(_("%s account configuration...") % system_info["user_name"])
        os.system('sed -i "s|# %wheel ALL=(ALL) ALL|%wheel ALL=(ALL) ALL|g" /mnt/etc/sudoers')
        if system_info["grml_zsh"]:
            os.system(
                f'arch-chroot /mnt bash -c "useradd --shell=/bin/zsh --groups=wheel --create-home {system_info["user_name"]}"')
        else:
            os.system(
                f'arch-chroot /mnt bash -c "useradd --shell=/bin/bash --groups=wheel --create-home {system_info["user_name"]}"')
        if system_info["user_full_name"] != "":
            os.system(
                f'arch-chroot /mnt bash -c "chfn -f \'{system_info["user_full_name"]}\' {system_info["user_name"]}"')
        if system_info["user_password"] != "":
            os.system(
                f'arch-chroot /mnt bash -c "echo \'{system_info["user_name"]}:{system_info["user_password"]}\' | chpasswd"')

    umount_partitions(swap_partition, swapfile_size)

    print_step(_("Installation complete ! You can reboot your system."), clear=False)


def pre_launch_steps():
    """
    The method to proceed to the pre-launch steps
    :return:
    """
    print_step("Running pre-launch steps : ", clear=False)
    print_sub_step("Synchronising repositories...")
    os.system("pacman -Sy &>/dev/null")
    print_sub_step("Downloading and formatting translations...")
    if not os.path.exists("fr.po"):
        urllib.request.urlretrieve("https://raw.githubusercontent.com/rawleenc/archlinux-install/dev/locales/fr.po",
                                   "fr.po")
    os.system('msgfmt -o /usr/share/locale/fr/LC_MESSAGES/archlinux-install.mo fr.po &>/dev/null')
    print_sub_step("Querying IP geolocation informations...")
    with urllib.request.urlopen('https://ipapi.co/json') as response:
        geoip_info = json.loads(response.read())
    detected_language = str(geoip_info["languages"]).split(",", maxsplit=1)[0]
    detected_timezone = geoip_info["timezone"]
    detected_country_code = geoip_info["country_code"]
    bios, global_language, keymap = environment_config(detected_language)
    locale_setup(keymap=keymap, global_language=global_language)
    return bios, detected_country_code, detected_timezone, global_language, keymap


if __name__ == '__main__':
    _ = gettext.gettext
    BIOS, DETECTED_COUNTRE_CODE, DETECTED_TIMEZONE, GLOBAL_LANGUAGE, KEYMAP = pre_launch_steps()
    if GLOBAL_LANGUAGE != "EN":
        translation = gettext.translation('archlinux-install', localedir='/usr/share/locale',
                                          languages=[GLOBAL_LANGUAGE.lower()])
        translation.install()
        _ = translation.gettext
    main(BIOS, DETECTED_COUNTRE_CODE, DETECTED_TIMEZONE, GLOBAL_LANGUAGE, KEYMAP)