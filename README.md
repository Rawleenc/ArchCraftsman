# ArchCraftsman

[![archlinux](https://img.shields.io/badge/-Arch%20Linux-grey?logo=archlinux)](https://archlinux.org)
[![usage](https://img.shields.io/badge/Usage-Installation%20script-1693d0)](https://wiki.archlinux.org/title/Installation_guide)
[![release](https://img.shields.io/github/tag/rawleenc/ArchCraftsman?label=Release)](https://github.com/rawleenc/ArchCraftsman/releases)

# Time to say goodbye

When this installer was created it was primarily intended to be used by myself.

I published it because I believe it can be useful to other people but I'm no longer an Archlinux user.

Moreover, with the development of the official Archinstall project, this kind of installer is not longer very useful. So I took the decision to archive this repository and to shutdown redirection links I setup to quickly run the installer.

Many thanks to all those who have supported, liked or even used this project. Fair winds to you on your linux journey!

# Usage

### On the Arch Linux live iso :

```bash
curl -O https://raw.githubusercontent.com/Rawleenc/ArchCraftsman/main/launcher.py
python launcher.py
```

Answer the questions and let the magic happen ;)

# Test

If you want to only test the script, you can clone it and then run it with this command :

```bash
python -m archcraftsman --install --test
```

It will simulate the execution of the script without changing anything to your system.

**Python 3.11 minimum is required.**

_Executing with root privilege or sudo installed is still required to gather disks information._

# Shell mode

ArchCraftsman can run in an interactive shell mode to manage bundles.  
The shell mode can be executed with this command :

```bash
python -m archcraftsman --shell
```

The shell mode is compatible with the test mode.

# Translations

To create new translations or update existing ones, first run the following command :

```bash
python /usr/lib/pythonX.Y/Tools/i18n/pygettext.py -d base -o base.pot archcraftsman
```

Then use [Poedit](https://archlinux.org/packages/community/x86_64/poedit/) to create or update translations based on the newly generated `base.pot`

# Requirements

ArchCraftsman is a pure native python 3 project based on the Archlinux's distribution of python. Therefore, it doesn't require any external dependencies to be executed. There is also no dependencies on the pypi.org package.

The requirements.txt file is only used for linting, formating, licensing, building, publishing, etc.

# Operation details and purpose

The purpose of this script is to propose a very fast and straightforward Arch Linux installation while bringing all the care I put on my own installations. The customization options are therefore not countless. However, some flexibility is still proposed.  
This script supports both UEFI and BIOS.

## Installation startup

At the very beginning, some information will be gathered using your IP address with [ipapi.co](https://ipapi.co/) API in order to propose more relevant default values :

- Language, to propose an adapted default global language and keymap
- Timezone, to propose an adapted default value for the timezone

## System setup

Then, a few questions will be asked to you to customize your installation.  
During this step, you'll be able to answer two types of questions :

- Yes/No questions.
- Choice questions.

In choice questions, you'll benefit from a smart and situation adapated auto-completion system to allow you to quickly get the option you want by pressing `tab`.

Packages included in the base :

```
base base-devel linux-firmware {linux kernel and headers}
```

Extra packages included :

```
intel-ucode/amd-ucode man-db man-pages (man-pages-{locale}) texinfo nano vim git curl os-prober efibootmgr xdg-user-dirs reflector numlockx net-tools polkit pacman-contrib
```

Required bundles :

- Kernel (linux, linux-lts, linux-zen or linux-hardened)
- Network stack (networkmanager, iwd and systemd or systemd only)

Optional packages bundles are also available, like for example :

- Desktop environment (Gnome, KDE Plasma or XFCE)
- Nvidia proprietary driver
- Cups
- Zsh with GRML config
- Main fonts
- Main file systems support
- ZRAM
- Pipewire

Time will be synchronized using systemd timesyncd.

Optionally an additional user, added to the wheel group and sudo configured to allow members of the wheel group.

Finally, you'll have two differents partitioning options. An automatic one and a manual one.

## The automatic partitioning

It is, for now, very simple :  
You'll have to choose the drive where you want to install Arch Linux, you'll be able to choose to have a swap in a file or in a partition and you'll be able to get a separated home or not.

**IMPORTANT :** If you are in UEFI mode, if you already have an installed system on the target drive and at least 32G of free space at the end of it, the automatic partitioning will detect it and will propose to install Arch Linux next to the existing system.  
If you don't want the dualboot or if you are in **BIOS** mode, the automatic partitioning will wipe the entire target drive to install Arch Linux.

Partitions sizes are determined as follows :

- EFI : 512M (In UEFI mode only)
- Boot : 1G (In BIOS mode only)
- Swap : 1/32 of the total drive size or 1/32 of the remaining free space in case of dualboot
- Root : All the rest of available space if no separated home, else 1/4 of the total drive size or 1/4 of the remaining free space in case of dualboot
- Home : All the rest of available space (if separated home only)

## The manual partitioning

It is the default most flexible and powerful option :  
The cfdisk tool will be proposed to you to partition your drives. You can create as many partitions as you want on as many drive as you want. Main partitions are the EFI partition, the Root partition, the Swap partition and the Home partition.

You will then have the possibility to choose to format or not the EFI and Home partitions, and for all other partitions, you will be able to choose the mount point and if you wish to format or not.

Normally, only Linux related partitions should be detected. However, if the detected partitions contain one that you don't want to use, you'll be able to tell the script that a partition will not be used.

## Partitions formats

For both partitioning options you will have the possibility to choose the partition format you want between the following ones :

- btrfs
- ext4

The BTRFS format is the default format and is completely integrated.

In automatic partitioning, the chosen format type will be applied for all partitions except the EFI partition.  
In manual partitioning you will be able to choose the format type to use for each partition individually except for the EFI partition.

If the EFI partition has to be formatted it will be formatted in vfat, otherwise the script expects the EFI partition to be already formatted in vfat (this is the case for Windows 10 for example).

All other partitions will be formatted in the format you want.

If you choose to not create a Swap partition, you will be proposed a swapfile of the size you want, called swapfile. It will be created and placed at the base of the Root partition. If you specify 0 for the swapfile size, no swap will be created.

Swapfile is not supported on a BTRFS root partition.

## Encryption

ArchCraftsman is able to encrypt any partitions you want using dm-crypt + LUKS on partitions.  
Cf. [LUKS on a partition](https://wiki.archlinux.org/title/Dm-crypt/Encrypting_an_entire_system#LUKS_on_a_partition).

If you choose to encrypt the root partition, then you'll need to have a /boot separated partition in order to be able to boot the system. During the format step, cryptsetup will be used leading to prompts asking you to enter a password for each partition you want to encrypt. These passwords will be asked to you during the boot to unlock your system.

During boot time, encrypted root partition will be unlocked by the kernel and all other encrypted partitions will be unlocked by systemd.

## Configuration file

A successful installation will create a configuration file in the user home or in `/root` that will contain all the information you provided during the installation.

This configuration file can be used to reinstall Arch Linux with the same configuration by using the --config option of the installer or directly in the launcher by entering the relative file path or a download url in the related question that will be asked to you. You can also skip this question to launch a standard interactive installation.

An installation with a configuration file will be fully automatic, without any required interactions, it will just install Arch Linux with the configuration you provided.

**WARNING :** Please make sure your configuration file is correct. Specifically, make sure the partitioning informations match the computer you are installing Arch Linux on. If there is any issue in the configuration file, it is very likely that the installation will crash without telling you why

A new configuration file can be generated in the shell mode on an existing archlinux system by using the `generateconfig` shell bundle.

Some configuration file examples are available in the [configs](configs) folder. These configuration files are examples of few typical possible installations. They are working on qemu/kvm virtual machines.

# Disclaimer

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  
See the [GNU General Public License](LICENSE.txt) for more details.
