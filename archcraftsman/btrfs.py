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

subvolumes = ["/var", "/opt", "/srv", "/tmp", "/root", "/usr/local", "/home"]


def get_packages():
    """
    A function to get the packages needed to install BTRFS.
    """
    return ["btrfs-progs", "grub-btrfs", "snapper", "snap-pac"]


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
        f'mount --mkdir -o compress=zstd "{path}" "/mnt{mount_point}"'
    )


def formatting(path: str, mount_point: str, part_mount_points: list[str]):
    """
    A function to format a partition.
    """
    _formatting(path)
    if mount_point == "/":
        _mount(path, mount_point)
        archcraftsman.base.execute("btrfs subvolume create /mnt/@")
        for subvolume in subvolumes:
            if subvolume not in part_mount_points:
                archcraftsman.base.execute(
                    f"btrfs subvolume create -p /mnt/@{subvolume}"
                )
        archcraftsman.base.execute("umount -R /mnt")


def mount(path: str, mount_point: str, part_mount_points: list[str]):
    """
    A function to mount the root partition.
    """
    _mount(path, mount_point)
    if mount_point == "/":
        for subvolume in subvolumes:
            if subvolume not in part_mount_points:
                archcraftsman.base.execute(
                    f"mount -o compress=zstd,subvol=@{subvolume} {path} /mnt{subvolume}"
                )


def configure():
    """
    A function to configure snapshots.
    """
    archcraftsman.base.execute("snapper --no-dbus -c root create-config /", chroot=True)
    archcraftsman.base.execute(
        "snapper --no-dbus -c root set-config TIMELINE_CREATE=no", chroot=True
    )
    archcraftsman.base.execute("systemctl enable snapper-cleanup.timer", chroot=True)
    archcraftsman.base.execute(
        "snapper --no-dbus create --description init", chroot=True
    )
