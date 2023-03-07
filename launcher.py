"""
The ArchCraftsman entry point. A launcher to download all ArchCraftsman's modules and run it.
"""
import json
import multiprocessing
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlretrieve, urlopen

OWNER = "Rawleenc"
REPO = "ArchCraftsman"
BRANCH = "main"
CMD = 'python -m src.archcraftsman --install'
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
        subprocess.run("/bin/clear", shell=True, check=True)
    print(f'\n{GREEN}{message}{NOCOLOR}')


def print_sub_step(message: str):
    """
    A method to print a sub step message.
    :param message:
    :return:
    """
    print(f'{CYAN}  * {message}{NOCOLOR}')


def download(url: str, destination: str, replace: bool = False):
    """
    A method to download a file
    :param url: the url of the file to download
    :param destination: the download destination
    :param replace: if any existing file have to be replaced
    :return:
    """
    print_sub_step(f"Downloading '{destination}'...")
    if replace and os.path.exists(destination):
        subprocess.run(f"rm -rf {destination}", shell=True, check=True)
    if not os.path.exists(destination):
        parent = os.path.dirname(destination)
        if parent:
            subprocess.run(f"mkdir -p {parent}", shell=True, check=True)
        urlretrieve(url, destination)


def get_all_files(directory: str) -> []:
    """
    A method to download all files of a given directory.
    :param directory:
    :return:
    """
    with urlopen(f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{directory}?ref={BRANCH}") as response:
        components = json.loads(response.read())
    files = []
    if components:
        for component in components:
            if component["type"] == "dir":
                for file in get_all_files(component["path"]):
                    files.append(file)
            elif component["type"] == "file":
                files.append(component)
    return files


if __name__ == '__main__':
    print_step("Downloading all ArchCraftsman's modules and locales...", clear=False)

    module_files = []
    for module_file in get_all_files("src"):
        module_files.append(module_file)
    for module_file in get_all_files("locales"):
        module_files.append(module_file)

    cpus = multiprocessing.cpu_count()
    with ThreadPoolExecutor(max_workers=cpus) as exe:
        futures = []
        for module_file in module_files:
            exe.submit(download, module_file["download_url"], module_file["path"], True)
        for future in as_completed(futures):
            future.result()

    try:
        subprocess.run(CMD, shell=True, check=True)
    except KeyboardInterrupt:
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
