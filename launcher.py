"""
The ArchCraftsman entry point. A launcher to download all ArchCraftsman's modules and run it.
"""
import multiprocessing
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlretrieve

from src.utils import execute

REPO_BASE_URL = "https://raw.githubusercontent.com/rawleenc/ArchCraftsman/dev"
CMD = 'python -m src.archcraftsman'
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
NOCOLOR = "\033[0m"


def print_step(message: str, clear: bool = True):
    """
    A method to print a step message.
    :param message:
    :param clear:
    """
    if clear:
        execute('clear', force=True)
    print(f'\n{GREEN}{message}{NOCOLOR}')


def print_sub_step(message: str):
    """
    A method to print a sub step message.
    :param message:
    :return:
    """
    print(f'{CYAN}  * {message}{NOCOLOR}')


def download(file_path: str, destination: str, replace: bool = False):
    """
    A method to download a file
    :param file_path: the file to download
    :param destination: the download destination
    :param replace: if any existing file have to be replaced
    :return:
    """
    print_sub_step(f"Downloading '{file_path}'...")
    if replace and os.path.exists(destination):
        execute(f"rm -rf {destination}")
    if not os.path.exists(destination):
        parent = os.path.dirname(destination)
        if parent:
            execute(f"mkdir -p {parent}")
        urlretrieve(f"{REPO_BASE_URL}/{file_path}", destination)


if __name__ == '__main__':
    print_step("Downloading all ArchCraftsman's modules and locales...", clear=False)
    download("modules_list", "modules_list", replace=True)
    with open('modules_list', 'r', encoding="UTF-8") as modules_list_file:
        module_files = modules_list_file.readlines()

    cpus = multiprocessing.cpu_count()
    with ThreadPoolExecutor(max_workers=cpus) as exe:
        futures = []
        for module_file in module_files:
            line = module_file.strip()
            exe.submit(download, line, line, True)
        for future in as_completed(futures):
            future.result()

    download("locales/fr.po", "fr.po")
    execute('msgfmt -o /usr/share/locale/fr/LC_MESSAGES/ArchCraftsman.mo fr.po &>/dev/null')

    try:
        subprocess.run(CMD, shell=True, check=True)
    except KeyboardInterrupt:
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
