# Archlinux Install

[![archlinux](https://img.shields.io/badge/-Arch%20Linux-grey?logo=archlinux)](https://archlinux.org)
[![usage](https://img.shields.io/badge/Usage-Installation%20script-1693d0)](https://wiki.archlinux.org/title/Installation_guide)
[![release](https://img.shields.io/github/v/tag/rawleenc/archlinux-install?label=Release)](https://github.com/rawleenc/archlinux-install/releases)
[![main workflow](https://github.com/rawleenc/archlinux-install/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/rawleenc/archlinux-install/actions)
[![dev workflow](https://github.com/rawleenc/archlinux-install/actions/workflows/main.yml/badge.svg?branch=dev)](https://github.com/rawleenc/archlinux-install/actions)


# Purpose

The purpose of this script is to install Arch Linux very quickly. The customization options are therefore not numerous. However, some flexibility is still allowed.  
This script supports both UEFI and BIOS.  

A manual partitioning of the target drive will be proposed with the cfdisk tool.

You can create as many partitions as you want on the target drive. Main partitions are the EFI partition, the Root partition, the Swap partition and the Home partition.  
You will have the possibility to choose to format or not the EFI and Home partitions, and for all other partitions, you will be able to choose the mount point and if you wish to format or not.

If the EFI partition has to be formatted it will be formatted in vfat, otherwise the script expects the EFI partition to be already formatted in vfat (this is the case for windows 10 for example) and all other partitions will be formatted in ext4. If you choose to not create a Swap partition, you will be proposed a swapfile of the size you want, called swapfile. It will be created and placed at the base of the Root partition.

Packages included in the base :  
`base base-devel linux-firmware man-db man-pages texinfo nano vim git curl grub os-prober efibootmgr networkmanager xdg-user-dirs reflector numlockx ntp`

Optional packages available :  
`intel-ucode amd-ucode linux/linux-lts nvidia/nvidia-lts terminus-font`

Optional packages bundles are also available :
- Desktop environment (Gnome, KDE Plasma or XFCE)
- Cups
- Zsh with GRML config
- Main fonts
- Main file systems support

Optionally an additional user, added to the wheel group and sudo configured to allow members of the wheel group.

# Usage

### On the Arch Linux live iso :
```bash
bash <(curl -L git.io/JKreg)
```

If you wish to test the latest development version, you can download it with this command :
```bash
bash <(curl -L git.io/JKlY5)
```
*However, this is absolutely not recommended for any other purpose than tests.*

Answer the questions and let the magic happen ;)

# Disclaimer

archlinux-install  Copyright (C) 2021  Rawleenc  

This program comes with ABSOLUTELY NO WARRANTY; See the [GNU General Public License](LICENSE) for more details.  

This is free software, and you are welcome to redistribute it
under certain conditions; See the [GNU General Public License](LICENSE) for more details.  
