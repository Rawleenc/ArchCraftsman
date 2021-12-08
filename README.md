# Archlinux Install

[![archlinux](https://img.shields.io/badge/-Arch%20Linux-grey?logo=archlinux)](https://archlinux.org)
[![usage](https://img.shields.io/badge/Usage-Installation%20script-1693d0)](https://wiki.archlinux.org/title/Installation_guide)
[![release](https://img.shields.io/github/tag/rawleenc/archlinux-install?label=Release)](https://github.com/rawleenc/archlinux-install/releases)
[![main workflow](https://github.com/rawleenc/archlinux-install/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/rawleenc/archlinux-install/actions)
[![dev workflow](https://github.com/rawleenc/archlinux-install/actions/workflows/main.yml/badge.svg?branch=dev)](https://github.com/rawleenc/archlinux-install/actions)


# Purpose

The purpose of this script is to install Arch Linux very quickly. The customization options are therefore not numerous. However, some flexibility is still allowed.  
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

If the EFI partition has to be formatted it will be formatted in vfat, otherwise the script expects the EFI partition to be already formatted in vfat (this is the case for windows 10 for example) and all other partitions will be formatted in ext4. If you choose to not create a Swap partition, you will be proposed a swapfile of the size you want, called swapfile. It will be created and placed at the base of the Root partition.

Packages included in the base :  
`base base-devel linux-firmware man-db man-pages texinfo nano vim git curl grub os-prober efibootmgr networkmanager xdg-user-dirs reflector numlockx ntp net-tools`

Optional packages available :  
`intel-ucode amd-ucode linux/linux-lts nvidia/nvidia-lts terminus-font`

Optional packages bundles are also available :
- Desktop environment (Gnome, KDE Plasma, XFCE, Budgie, Cinnamon, CuteFish, Deepin, LxQT, Mate, Enlightenment, i3 or Sway)
- Cups
- Zsh with GRML config
- Main fonts
- Main file systems support

**Warning :** Sway doesn't start in a virtual machine nor with the Nvidia proprietary driver, but it works in a physical install with an Intel or AMD GPU.

Some informations will be gathered using your IP address with ipapi.co API in order to propose more relevant default values for prompts and better mirror sorting :  
- Language, to propose an adapted default global language and keymap
- Country code, to propose a better mirror sorting
- Timezone, to propose an adapted default value for the timezone

Time will be synchronized using ntpd.

Optionally an additional user, added to the wheel group and sudo configured to allow members of the wheel group.

# Usage

### On the Arch Linux live iso :
```bash
python <(curl -L git.io/JXjXG)
```

If you wish to test the latest development version, you can run it with this command :
```bash
python <(curl -L git.io/JXFOn)
```
*However, this is absolutely not recommended for any other purpose than tests.*

Answer the questions and let the magic happen ;)

# Disclaimer

archlinux-install  Copyright (C) 2021  Rawleenc  

This program comes with ABSOLUTELY NO WARRANTY; See the [GNU General Public License](LICENSE) for more details.  

This is free software, and you are welcome to redistribute it
under certain conditions; See the [GNU General Public License](LICENSE) for more details.  
