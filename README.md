# Objectif

Le but de ce script est d'installer une base Arch Linux exactement comme MOI je l'aime, très rapidement.  
Vous n'aurez du coup pas beaucoup d'options de personnalisation. Donc si c'est ce que vous recherchez, passez votre chemin.  
Ce script fonctionne uniquement sur un firmware UEFI.

Un partitionnement du disque spécifié sera proposé avec l'outil cfdisk.

Le script s'attend à avoir deux partitions seulement :
- Une partition EFI System, elle sera montée sur /boot/efi
- Une partition Linux Root, elle sera montée sur /

Si la partition EFI doit être formatée elle le sera en vfat, sinon le script s'attend à ce que la partition EFI soit déjà formatée en vfat (C'est le cas pour windows 10 par exemple), la partition root sera formatée en ext4 et un swapfile de la taille spécifiée, appelé swapfile, sera créé et placé à la racine de la partition Root.

Paquets inclues dans la base :  
*base base-devel linux linux-firmware man-db man-pages texinfo nano vim git curl zsh zsh-completions grml-zsh-config grub os-prober efibootmgr networkmanager xdg-user-dirs*

Shell par défaut : ZSH avec la config GRML.  
Éventuellement un utilisateur supplémentaire, ajouté au groupe wheel et sudo configuré pour autoriser les membres du groupe wheel.

# Utilisation

### Sur l'iso live de Arch Linux :
bash <(curl -L https://github.com/rawleenc/archlinux-install/releases/download/1.6.0/archlinux-install)

Répondez aux questions et laissez la magie opérer ! ;)
