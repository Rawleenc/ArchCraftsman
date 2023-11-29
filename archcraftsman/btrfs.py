# ArchCraftsman, The careful yet very fast Arch Linux Craftsman.
# Copyright (C) 2023 Rawleenc
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
All BTRFS related functions
"""

import archcraftsman.base


class Subvolume:
    """
    A class to represent a subvolume.
    """

    def __init__(self, name: str, path: str, compression: str = ""):
        self.name = name
        self.path = path
        self.compression = compression

    def create(self):
        """
        A method to create a subvolume.
        """
        archcraftsman.base.execute(f"btrfs subvolume create -p /mnt/{self.name}")

    def mount(self, partition: str):
        """
        A method to mount a subvolume.
        """
        compression = f"compress={self.compression}," if self.compression else ""
        archcraftsman.base.execute(
            f"mount --mkdir -o {compression}subvol={self.name} {partition} /mnt{self.path}"
        )


SNAPSHOTS_SUBVOLUME = Subvolume("@snapshots", "/.snapshots", "zstd")
SWAP_SUBVOLUME = Subvolume("@swap", "/swap")


subvolumes = [
    Subvolume("@var", "/var", "zstd"),
    Subvolume("@opt", "/opt", "zstd"),
    Subvolume("@srv", "/srv", "zstd"),
    Subvolume("@tmp", "/tmp", "zstd"),
    Subvolume("@root", "/root", "zstd"),
    Subvolume("@usr_local", "/usr/local", "zstd"),
    Subvolume("@home", "/home", "zstd"),
    SWAP_SUBVOLUME,
    SNAPSHOTS_SUBVOLUME,
]


def get_packages():
    """
    A function to get the packages needed to support BTRFS format.
    """
    return ["btrfs-progs"]


def get_management_packages():
    """
    A function to get the packages needed to manage a BTRFS root filesystem.
    """
    return ["grub-btrfs", "snapper", "snap-pac", "inotify-tools"]


def _formatting(path: str):
    """
    A function to format a partition.
    """
    archcraftsman.base.execute(f"mkfs.btrfs -f {path}")


def _mount(path: str, mount_point: str):
    """
    A function to mount a partition.
    """
    archcraftsman.base.execute(
        f"mount --mkdir -o compress=zstd {path} /mnt{mount_point}"
    )


def formatting(path: str, mount_point: str, part_mount_points: list[str]):
    """
    A function to format a partition.
    """
    _formatting(path)
    if mount_point == "/":
        _mount(path, "/")
        archcraftsman.base.execute("btrfs subvolume create /mnt/@")
        archcraftsman.base.execute("btrfs subvolume set-default /mnt/@")
        for subvolume in subvolumes:
            if subvolume.path not in part_mount_points:
                subvolume.create()
        archcraftsman.base.execute("umount -R /mnt")


def mount(path: str, mount_point: str, part_mount_points: list[str]):
    """
    A function to mount the root partition.
    """
    _mount(path, mount_point)
    if mount_point == "/":
        for subvolume in subvolumes:
            if subvolume.name == "@snapshots":
                continue
            if subvolume.path not in part_mount_points:
                subvolume.mount(path)


def create_swapfile(size: str):
    """
    A function to create a BTRFS swapfile.
    """
    archcraftsman.base.execute(
        f"btrfs filesystem mkswapfile --size {size} --uuid clear /mnt/swap/swapfile"
    )


def configure(path: str):
    """
    A function to configure snapshots.
    """
    archcraftsman.base.execute("snapper --no-dbus -c root create-config /", chroot=True)
    archcraftsman.base.execute(
        "snapper --no-dbus -c root set-config TIMELINE_CREATE=no", chroot=True
    )

    archcraftsman.base.execute("systemctl enable snapper-cleanup.timer", chroot=True)
    archcraftsman.base.execute("systemctl enable grub-btrfsd.service", chroot=True)

    archcraftsman.base.execute(f"btrfs subvolume delete /mnt{SNAPSHOTS_SUBVOLUME.path}")
    archcraftsman.base.execute(f"mkdir /mnt{SNAPSHOTS_SUBVOLUME.path}")
    SNAPSHOTS_SUBVOLUME.mount(path)
    archcraftsman.base.execute(f"chmod 750 /mnt{SNAPSHOTS_SUBVOLUME.path}")

    archcraftsman.base.execute(
        'snapper --no-dbus create --read-write --description "Installation finished."',
        chroot=True,
    )

    archcraftsman.base.execute("grub-mkconfig -o /boot/grub/grub.cfg", chroot=True)
