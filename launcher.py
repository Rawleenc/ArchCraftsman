"""
The ArchCraftsman entry point. A launcher to download all ArchCraftsman's modules and run it.
"""
import multiprocessing
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlretrieve

REPO_BASE_URL = "https://raw.githubusercontent.com/rawleenc/ArchCraftsman/dev"
CMD = 'python -m src.archcraftsman'


def download(file_path: str, destination: str, replace: bool = False):
    """
    A method to download a file
    :param file_path: the file to download
    :param destination: the download destination
    :param replace: if any existing file have to be replaced
    :return:
    """
    print(f"Downloading '{file_path}'...")
    if replace and os.path.exists(destination):
        os.system(f"rm -rf {destination}")
    if not os.path.exists(destination):
        parent = os.path.dirname(destination)
        if parent:
            os.system(f"mkdir -p {parent}")
        urlretrieve(f"{REPO_BASE_URL}/{file_path}", destination)


if __name__ == '__main__':
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
    os.system('msgfmt -o /usr/share/locale/fr/LC_MESSAGES/ArchCraftsman.mo fr.po &>/dev/null')

    try:
        subprocess.run(CMD, shell=True, check=True)
    except KeyboardInterrupt:
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
