import os
import subprocess
import urllib.request

REPO_BASE_URL = "https://raw.githubusercontent.com/rawleenc/ArchCraftsman/splitting"
CMD = 'python -m src.archcraftsman'


def download_if_not_exist(file_name: str, destination: str):
    print(f"Downloading '{file_name}'...")
    if not os.path.exists(destination):
        parent = os.path.dirname(destination)
        if parent:
            os.makedirs(parent)
        urllib.request.urlretrieve(f"{REPO_BASE_URL}/{file_name}", destination)


if __name__ == '__main__':
    download_if_not_exist("modules_list", "modules_list")
    modules_list_file = open('modules_list', 'r')
    module_files = modules_list_file.readlines()
    for module_file in module_files:
        line = module_file.strip()
        download_if_not_exist(line, line)

    download_if_not_exist("locales/fr.po", "fr.po")
    os.system('msgfmt -o /usr/share/locale/fr/LC_MESSAGES/ArchCraftsman.mo fr.po &>/dev/null')

    p = subprocess.Popen(CMD, stdout=subprocess.PIPE, shell=True)

    out, err = p.communicate()
    result = out.splitlines()
    for line in result:
        print(line)
