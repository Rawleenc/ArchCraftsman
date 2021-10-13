# Purpose

The purpose of this script is to install Arch Linux very quickly. The customization options are therefore not numerous. However, some flexibility is still allowed.  
This script supports both UEFI and BIOS.  

A manual partitioning of the target drive will be proposed with the cfdisk tool.

You can create as many partitions as you want on the target drive except for the swap partition. Main partitions are the EFI partition, the Root partition and the Home partition.  
You will have the possibility to choose to format or not the EFI and Home partitions, and for all other partitions, you will be able to choose the mount point and if you wish to format or not.

If the EFI partition has to be formatted it will be formatted in vfat, otherwise the script expects the EFI partition to be already formatted in vfat (this is the case for windows 10 for example) and all other partitions will be formatted in ext4. Concerning the swap, a swapfile of the specified size, called swapfile, will be created and placed at the base of the Root partition.

Packages included in the base :  
`base base-devel linux-firmware man-db man-pages texinfo nano vim git curl grub os-prober efibootmgr networkmanager xdg-user-dirs`

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

## On the Arch Linux live iso :
```bash
bash <(curl -L git.io/JoiIR)
```

If you wish to use the previous version, you can download the latest patch with this command :
```bash
bash <(curl -L git.io/Jo6K4)
```
*Keep in mind that the previous version maybe be quicker but it is in french only and provide less flexibiliy than the latest version.*

If you wish to test the latest development version, follow these steps :
```bash
pacman -Sy unzip
curl -L github.com/rawleenc/archlinux-install/archive/refs/heads/master.zip > master.zip
unzip master.zip
./archlinux-install-master/archlinux-install
```
*However, this is absolutely not recommended for any other purpose than tests.*

Answer the questions and let the magic happen ;)

# Disclaimer

archlinux-install  Copyright (C) 2021  Rawleenc  

This program comes with ABSOLUTELY NO WARRANTY; See the [GNU General Public License](LICENSE) for more details.  

This is free software, and you are welcome to redistribute it
under certain conditions; See the [GNU General Public License](LICENSE) for more details.  
