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

import datetime

import archcraftsman.base


class Subvolume:
    """
    A class to represent a subvolume.
    """

    def __init__(self, path: str, compression: str = "zstd"):
        self.path = path
        self.compression = compression

    def create(self):
        """
        A method to create a subvolume.
        """
        archcraftsman.base.execute(f"btrfs subvolume create -p /mnt/@{self.path}")

    def mount(self, partition: str):
        """
        A method to mount a subvolume.
        """
        compression = f"compress={self.compression}," if self.compression else ""
        archcraftsman.base.execute(
            f"mount --mkdir -o {compression}subvol=@{self.path} {partition} /mnt{self.path}"
        )


SNAPSHOTS_SUBVOLUME = Subvolume("/.snapshots")
SWAP_SUBVOLUME = Subvolume("/swap", compression="")


subvolumes = [
    Subvolume("/var"),
    Subvolume("/opt"),
    Subvolume("/srv"),
    Subvolume("/tmp"),
    Subvolume("/root"),
    Subvolume("/usr/local"),
    Subvolume("/home"),
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
        for subvolume in subvolumes:
            if subvolume.path not in part_mount_points:
                subvolume.create()
        archcraftsman.base.execute(
            f"btrfs subvolume create -p /mnt/@{SNAPSHOTS_SUBVOLUME.path}/1/snapshot"
        )
        now = datetime.datetime.now()
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")
        content = [
            '<?xml version="1.0"?>\n',
            "<snapshot>\n",
            "  <type>single</type>\n",
            "  <num>1</num>\n",
            f"  <date>{formatted_date}</date>\n",
            "  <description>Initial snapshot.</description>\n",
            "</snapshot>\n",
        ]
        with open(
            f"/mnt/@{SNAPSHOTS_SUBVOLUME.path}/1/info.xml", "w", encoding="UTF-8"
        ) as first_snapshot_info_file:
            first_snapshot_info_file.writelines(content)
        archcraftsman.base.execute(
            f"btrfs subvolume set-default /mnt/@{SNAPSHOTS_SUBVOLUME.path}/1/snapshot"
        )
        archcraftsman.base.execute("umount -R /mnt")


def mount(path: str, mount_point: str, part_mount_points: list[str]):
    """
    A function to mount the root partition.
    """
    _mount(path, mount_point)
    if mount_point == "/":
        for subvolume in subvolumes:
            if subvolume.path == SNAPSHOTS_SUBVOLUME.path:
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
