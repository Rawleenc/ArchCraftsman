# Objectif

Le but de ce script est d'installer une base Arch Linux exactement comme MOI je l'aime, très rapidement.  
Vous n'aurez du coup pas beaucoup d'options de personnalisation. Donc si c'est ce que vous recherchez, passez votre chemin.  
Ce script fonctionne uniquement sur un firmware UEFI.

**ATTENTION : Actuellement ce script EFFACE COMPLÈTEMENT le disque spécifié.**

La base Arch Linux installée est construite de la façon suivante :  
Sur le disque dur spécifié, deux partitions :
- 1Go - EFI System, monté sur /boot/efi
- Tout le reste - Linux Root, monté sur /
- Un swapfile de taille égale à la RAM, appelé swapfile, localisé sur /

Paquets inclues dans la base :  
*base base-devel linux linux-firmware man-db man-pages texinfo nano vim git curl zsh zsh-completions grml-zsh-config grub os-prober efibootmgr networkmanager xdg-user-dirs*

Shell par défaut : ZSH avec la config GRML.  
Éventuellement un utilisateur supplémentaire, ajouté au groupe wheel et sudo configuré pour autoriser les membres du groupe wheel.

# Utilisation

### Sur l'iso live de Arch Linux :
pacman -Sy wget  
wget https://github.com/rawleenc/archlinux-install/releases/download/{DERNIERE_VERSION}/archlinux-install  
./archlinux-install  

Répondez aux questions et laissez la magie opérer ! ;)
