# ArchCraftsman, The careful yet very fast Arch Linux Craftsman.
# Copyright (C) 2023 Rawleenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
The ArchCraftsman entry point. A launcher to download all ArchCraftsman's modules and run it.
"""
import json
import multiprocessing
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen, urlretrieve

OWNER = "Rawleenc"
REPO = "ArchCraftsman"
BRANCH = "dev"
CMD = "python -m archcraftsman.installer --install"
GREEN = "\033[0;32m"
CYAN = "\033[0;36m"
NOCOLOR = "\033[0m"


def print_step(message: str, clear: bool = True):
    """
    A method to print a step message.
    """
    if clear:
        subprocess.run("/bin/clear", shell=True, check=True)
    print(f"\n{GREEN}{message}{NOCOLOR}")


def print_sub_step(message: str):
    """
    A method to print a sub step message.
    """
    print(f"{CYAN}  * {message}{NOCOLOR}")


def download(url: str, destination: str, replace: bool = False):
    """
    A method to download a file
    """
    print_sub_step(f"Downloading '{destination}'...")
    if replace and os.path.exists(destination):
        subprocess.run(f"rm -rf {destination}", shell=True, check=True)
    if not os.path.exists(destination):
        parent = os.path.dirname(destination)
        if parent:
            subprocess.run(f"mkdir -p {parent}", shell=True, check=True)
        urlretrieve(url, destination)


def get_all_files(directory: str) -> list:
    """
    A method to download all files of a given directory.
    """
    with urlopen(
        f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{directory}?ref={BRANCH}"
    ) as response:
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


if __name__ == "__main__":
    print_step("Downloading all ArchCraftsman's modules...", clear=False)

    module_files = []
    for module_file in get_all_files("archcraftsman"):
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
