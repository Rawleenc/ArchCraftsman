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

SNAPSHOTS_SUBVOLUME = "@snapshots"

subvolumes = {
    "@var": "/var",
    "@opt": "/opt",
    "@srv": "/srv",
    "@tmp": "/tmp",
    "@root": "/root",
    "@usr_local": "/usr/local",
    "@home": "/home",
    SNAPSHOTS_SUBVOLUME: "/.snapshots",
}


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


def _mount_subvolume(path: str, mount_point: str, subvolume: str):
    """
    A function to mount a subvolume.
    """
    archcraftsman.base.execute(
        f"mount --mkdir -o compress=zstd,subvol={subvolume} {path} /mnt{mount_point}"
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
        for subvolume_name, subvolume_path in subvolumes.items():
            if subvolume_path not in part_mount_points:
                archcraftsman.base.execute(
                    f"btrfs subvolume create -p /mnt/{subvolume_name}"
                )
        archcraftsman.base.execute("umount -R /mnt")


def mount(path: str, mount_point: str, part_mount_points: list[str]):
    """
    A function to mount the root partition.
    """
    if mount_point == "/":
        _mount(path, "/")
        for subvolume_name, subvolume_path in subvolumes.items():
            if subvolume_name == "@snapshots":
                continue
            if subvolume_path not in part_mount_points:
                _mount_subvolume(path, subvolume_path, subvolume_name)
    else:
        _mount(path, mount_point)


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

    archcraftsman.base.execute(
        f"btrfs subvolume delete /mnt{subvolumes[SNAPSHOTS_SUBVOLUME]}"
    )
    archcraftsman.base.execute(f"mkdir /mnt{subvolumes[SNAPSHOTS_SUBVOLUME]}")
    _mount_subvolume(path, subvolumes[SNAPSHOTS_SUBVOLUME], SNAPSHOTS_SUBVOLUME)
    archcraftsman.base.execute(f"chmod 750 /mnt{subvolumes[SNAPSHOTS_SUBVOLUME]}")

    archcraftsman.base.execute(
        'snapper --no-dbus create --read-write --description "Installation finished."',
        chroot=True,
    )

    archcraftsman.base.execute("grub-mkconfig -o /boot/grub/grub.cfg", chroot=True)
