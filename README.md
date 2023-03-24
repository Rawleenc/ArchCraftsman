# ArchCraftsman

[![archlinux](https://img.shields.io/badge/-Arch%20Linux-grey?logo=archlinux)](https://archlinux.org)
[![usage](https://img.shields.io/badge/Usage-Installation%20script-1693d0)](https://wiki.archlinux.org/title/Installation_guide)
[![release](https://img.shields.io/github/tag/rawleenc/ArchCraftsman?label=Release)](https://github.com/rawleenc/ArchCraftsman/releases)
[![main workflow](https://github.com/rawleenc/ArchCraftsman/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/rawleenc/ArchCraftsman/actions)
[![dev workflow](https://github.com/rawleenc/ArchCraftsman/actions/workflows/main.yml/badge.svg?branch=dev)](https://github.com/rawleenc/ArchCraftsman/actions)

# Usage

### On the Arch Linux live iso :
```bash
python <(curl -L rotf.lol/acmain)
```

If you wish to test the latest development version, you can run it with this command :
```bash
python <(curl -L rotf.lol/acdev)
```
*However, this is absolutely not recommended for any other purpose than tests.*

Answer the questions and let the magic happen ;)

# Test

If you want to only test the script, you can clone it and then run it with this command :
```bash
sudo python -m archcraftsman.installer --install --test
```
It will simulate the execution of the script without changing anything to your system.

**Python 3.10 minimum is required.**

_Executing with root privilege is still required to gather disks information._

# Shell mode

ArchCraftsman can run in an interactive shell mode to manage bundles.  
The shell mode can be executed with this command :
```bash
sudo python -m archcraftsman.installer --shell
```
The shell mode is compatible with the test mode.

# Translations

To create new translations or update existing ones, first run the following command :
```bash
python /usr/lib/pythonX.Y/Tools/i18n/pygettext.py -d base -o base.pot archcraftsman
```
Then use [Poedit](https://archlinux.org/packages/community/x86_64/poedit/) to create or update translations based on the newly generated `base.pot`

# Purpose

The purpose of this script is to propose a very fast and straightforward Arch Linux installation while bringing all the care I put on my own installations. The customization options are therefore not countless. However, some flexibility is still proposed.  
This script supports both UEFI and BIOS.  

You'll have two differents partitioning options. An automatic one and a manual one.  

**The automatic partitioning** is, for now, very simple :  
You'll have to choose the drive where you want to install Arch Linux, you'll be able to choose to have a swap in a file or in a partition and you'll be able to get a separated home or not.  
**IMPORTANT :** If you are in UEFI mode, if you already have an installed system on the target drive and at least 32G of free space at the end of it, the automatic partitioning will detect it and will propose to install Arch Linux next to the existing system.  
If you don't want the dualboot or if you are in **BIOS** mode, the automatic partitioning will wipe the entire target drive to install Arch Linux.  
Partitions sizes are determined as follows :
- EFI : 512M (In UEFI mode only)
- Boot : 1G (In BIOS mode only)
- Swap : 1/32 of the total drive size or 1/32 of the remaining free space in case of dualboot
- Root : All the rest of available space if no separated home, else 1/4 of the total drive size or 1/4 of the remaining free space in case of dualboot
- Home : All the rest of available space (if separated home only)

**The manual paritioning** is the default most flexible and powerful option :  
The cfdisk tool will be proposed to you to partition your drives. You can create as many partitions as you want on as many drive as you want. Main partitions are the EFI partition, the Root partition, the Swap partition and the Home partition.  
You will then have the possibility to choose to format or not the EFI and Home partitions, and for all other partitions, you will be able to choose the mount point and if you wish to format or not.  

Normally, only Linux related partitions should be detected. However, if the detected partitions contain one that you don't want to use, you'll be able to tell the script that a partition will not be used.

For both partitioning options you will have the possibility to choose the partition format you want between the following ones :
- ext4
- btrfs

In automatic partitioning, the chosen format type will be applied for all partitions except the EFI partition.  
In manual partitioning you will be able to choose the format type to use for each partition individually except for the EFI partition.

If the EFI partition has to be formatted it will be formatted in vfat, otherwise the script expects the EFI partition to be already formatted in vfat (this is the case for Windows 10 for example) and all other partitions will be formatted in the format you want. If you choose to not create a Swap partition, you will be proposed a swapfile of the size you want, called swapfile. It will be created and placed at the base of the Root partition. If you specify 0 for the swapfile size, no swap will be created.

Packages included in the base :  
`base base-devel linux-firmware linux/linux-lts linux-headers/linux-lts-headers pacman-contrib man-db man-pages texinfo nano vim git curl grub os-prober efibootmgr networkmanager xdg-user-dirs reflector numlockx net-tools polkit`

Optional packages available :  
`intel-ucode amd-ucode nvidia/nvidia-lts terminus-font man-pages-{LOCALE}`

Optional packages bundles are also available :
- Desktop environment (Gnome, KDE Plasma, XFCE, Budgie, Cinnamon, CuteFish, Deepin, LxQT, Mate, Enlightenment, i3 or Sway)
- Cups
- Zsh with GRML config
- Main fonts
- Main file systems support
- ZRAM

**Warning :** Sway doesn't start in a virtual machine nor with the Nvidia proprietary driver, but it works in a physical installation with an Intel or AMD GPU.

Some information will be gathered using your IP address with ipapi.co API in order to propose more relevant default values for prompts and better mirror sorting :  
- Language, to propose an adapted default global language and keymap
- Timezone, to propose an adapted default value for the timezone

Time will be synchronized using systemd timesyncd.

Optionally an additional user, added to the wheel group and sudo configured to allow members of the wheel group.

# Disclaimer

ArchCraftsman  Copyright (C) 2022  Rawleenc  

This program comes with ABSOLUTELY NO WARRANTY; See the [GNU General Public License](LICENSE) for more details.  

This is free software, and you are welcome to redistribute it
under certain conditions; See the [GNU General Public License](LICENSE) for more details.  
