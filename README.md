# Purpose

The purpose of this script is to install an Arch Linux base very quickly. The customization options are therefore not numerous. However, some flexibility is still allowed.  
This script supports both UEFI and BIOS.  

A manual partitioning of the target drive will be proposed with the cfdisk tool.

You can create as many partitions as you want on the target drive except for the swap partition. Main partitions are the EFI partition, the Root partition and the Home partition.  
You will have the possibility to choose to format or not the EFI and Home partitions, and for all other partitions, you will be able to choose the mount point and if you wish to format or not.

If the EFI partition has to be formatted it will be formatted in vfat, otherwise the script expects the EFI partition to be already formatted in vfat (this is the case for windows 10 for example) and all other partitions will be formatted in ext4. Concerning the swap, a swapfile of the specified size, called swapfile, will be created and placed at the base of the Root partition.

Packages included in the base :  
`base base-devel linux-firmware man-db man-pages texinfo nano vim git curl zsh zsh-completions grml-zsh-config grub os-prober efibootmgr networkmanager xdg-user-dirs`

Optional packages available :  
`intel-ucode amd-ucode linux/linux-lts nvidia/nvidia-lts terminus-font`

Default shell: ZSH with GRML config.  
Optionally an additional user, added to the wheel group and sudo configured to allow members of the wheel group.

# Usage

## On the Arch Linux live iso :
bash <(curl -L github.com/rawleenc/archlinux-install/releases/download/1.7.0/archlinux-install)

Answer the questions and let the magic happen ;)
