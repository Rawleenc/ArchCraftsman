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
import concurrent.futures
import glob
import json
import multiprocessing
import os
import re
import readline
import subprocess
import sys
import urllib.error
import urllib.request

OWNER = "Rawleenc"
REPO = "ArchCraftsman"
BRANCH = "main"
CMD = "python -m archcraftsman.installer --install"
STEP = "\033[94m"
SUBSTEP = "\033[96m"
PROMPT = "\033[1m"
RESET = "\033[0m"


def print_step(message: str, clear: bool = True):
    """
    A method to print a step message.
    """
    if clear:
        subprocess.run("/bin/clear", shell=True, check=True)
    print(f"\n{STEP}{message}{RESET}")


def print_sub_step(message: str):
    """
    A method to print a sub step message.
    """
    print(f"{SUBSTEP}+ {message}{RESET}")


def input_str(message: str) -> str:
    """
    A method to ask to input something.
    """
    return input(f"{PROMPT}{message}{RESET}")


def glob_completer(text, state) -> str:
    """
    The glob completer for readline completions.
    """
    return [
        path + "/" if os.path.isdir(path) else path for path in glob.glob(text + "*")
    ][state]


def change_user_agent():
    """
    A method to change the user agent.
    """
    user_agent = "Mozilla/5.0 (Linux) ArchCraftsman"
    opener = urllib.request.build_opener()
    opener.addheaders = [("User-Agent", user_agent)]
    urllib.request.install_opener(opener)


def download_file(url, file_path) -> bool:
    """
    A method to stream download a single file.
    """
    if not re.match(r"^[a-zA-Z]+://", url):
        url = f"https://{url}"
    try:
        urllib.request.urlretrieve(url, file_path)
        return True
    except urllib.error.URLError:
        return False


def download(url: str, destination: str, replace: bool = False) -> bool:
    """
    A method to download a file
    """
    if not url:
        return False
    print_sub_step(f"Downloading '{destination}'...")
    if replace and os.path.exists(destination):
        subprocess.run(f"rm -rf {destination}", shell=True, check=True)
    if not os.path.exists(destination):
        parent = os.path.dirname(destination)
        if parent:
            subprocess.run(f"mkdir -p {parent}", shell=True, check=True)
        download_file(url, destination)
    if not os.path.exists(destination):
        return False
    return True


def get_all_files(directory: str) -> list:
    """
    A method to download all files of a given directory.
    """
    with urllib.request.urlopen(
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


def set_config_file(cmd: str, config_file: str) -> tuple[str, str]:
    """
    A recursive method to set the config file.
    """
    if os.path.exists(config_file):
        cmd += f" --config {config_file}"
    else:
        change_user_agent()
        download(config_file, "config.json", True)
        config_file = "config.json"
        if os.path.exists(config_file):
            cmd += f" --config {config_file}"
    return cmd, config_file


def main(cmd: str):
    """
    Main launcher function.
    """
    print_step("Downloading all ArchCraftsman's modules...", clear=False)
    readline.set_completer_delims(" \t\n;")
    readline.parse_and_bind("tab: complete")
    readline.set_completer(glob_completer)

    files = []
    for file in get_all_files("archcraftsman"):
        files.append(file)

    for file in get_all_files("configs"):
        files.append(file)

    cpus = multiprocessing.cpu_count()
    with concurrent.futures.ThreadPoolExecutor(max_workers=cpus) as exe:
        futures = []
        for module_file in files:
            exe.submit(download, module_file["download_url"], module_file["path"], True)
        for future in concurrent.futures.as_completed(futures):
            future.result()

    config_file = input_str(
        "Enter a config file path or url if you want to use one (leave empty to run interactive mode) : \n> "
    )
    cmd, config_file = set_config_file(cmd, config_file)

    if "--config" in cmd:
        edit = input_str("Do you want to edit the config file (with nano) ? (y/N) : ")
        if edit == "y":
            subprocess.run(
                "/bin/echo 'include /usr/share/nano/json.nanorc' > ~/.nanorc",
                shell=True,
                check=False,
            )
            subprocess.run(f"/bin/nano {config_file}", shell=True, check=False)

    try:
        subprocess.run(cmd, shell=True, check=True)
    except KeyboardInterrupt:
        sys.exit(1)
    except subprocess.CalledProcessError as exception:
        sys.exit(exception.returncode)


if __name__ == "__main__":
    main(CMD)
