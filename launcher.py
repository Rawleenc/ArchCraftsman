import multiprocessing
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlretrieve

REPO_BASE_URL = "https://raw.githubusercontent.com/rawleenc/ArchCraftsman/splitting"
CMD = 'python -m src.archcraftsman'


def download_if_not_exist(file_path: str, destination: str, replace: bool = False):
    print(f"Downloading '{file_path}'...")
    if replace and os.path.exists(destination):
        os.system(f"rm -rf {destination}")
    elif not os.path.exists(destination):
        parent = os.path.dirname(destination)
        if parent:
            os.system(f"mkdir -p {parent}")
        urlretrieve(f"{REPO_BASE_URL}/{file_path}", destination)


if __name__ == '__main__':
    download_if_not_exist("modules_list", "modules_list", replace=True)
    modules_list_file = open('modules_list', 'r')
    module_files = modules_list_file.readlines()

    cpus = multiprocessing.cpu_count()
    with ThreadPoolExecutor(max_workers=cpus) as exe:
        futures = []
        for module_file in module_files:
            line = module_file.strip()
            exe.submit(download_if_not_exist, line, line, True)
        for future in as_completed(futures):
            future.result()

    download_if_not_exist("locales/fr.po", "fr.po")
    os.system('msgfmt -o /usr/share/locale/fr/LC_MESSAGES/ArchCraftsman.mo fr.po &>/dev/null')

    subprocess.run(CMD, shell=True, check=True)
