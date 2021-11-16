import re
import os


class Partition:
    """
    A class to represent a partition.
    """
    path: str
    size: int
    part_type: str
    fs_type: str

    def __init__(self, part_str: str = None):
        """
        Partition initialisation.
        """
        if part_str is None:
            self.path = ""
            self.size = 0
            self.part_type = ""
            self.fs_type = ""
        else:
            self.path = part_str.split(" ")[0]
            self.size = from_iec(re.sub('\\s', '', os.popen(f'lsblk -nl "{self.path}" -o SIZE').read()))
            self.part_type = str(
                re.sub('[^a-zA-Z0-9 ]', '', os.popen(f'lsblk -nl "{self.path}" -o PARTTYPENAME').read()))
            self.fs_type = str(
                re.sub('[^a-zA-Z0-9 ]', '', os.popen(f'lsblk -nl "{self.path}" -o FSTYPE').read()))

    def __str__(self) -> str:
        """
        Partition str formatting.
        """
        return f"'{self.path}' - '{self.size}' - '{self.part_type}' - '{self.fs_type}'"


class Disk:
    """
    A partition to represent a disk.
    """
    path: str
    partitions: list
    total: int
    free_space: int

    def __init__(self, path: str):
        """
        Disk initialisation.
        """
        self.path = path
        detected_partitions = os.popen(f'lsblk -nl "{path}" -o PATH,TYPE | grep part').read()
        self.partitions = []
        for partition_info in detected_partitions.splitlines():
            self.partitions.append(Partition(partition_info))
        self.total = int(os.popen(f'lsblk -b --output SIZE -n -d "{self.path}"').read())
        if len(self.partitions) > 0:
            sector_size = int(
                re.sub('\\s', '',
                       os.popen(f'lsblk {path} -o PATH,TYPE,PHY-SEC | grep disk | awk \'{{print $3}}\'').read()))
            last_partition_path = [p.path for p in self.partitions][len(self.partitions) - 1]
            last_sector = int(
                re.sub('\\s', '', os.popen(f'fdisk -l | grep {last_partition_path} | awk \'{{print $3}}\'').read()))
            self.free_space = self.total - (last_sector * sector_size)
        else:
            self.free_space = self.total

    def get_efi_partition(self) -> Partition:
        """
        The Disk method to get the EFI partition if it exist. Else return an empty partition object.
        """
        try:
            return [p for p in self.partitions if "EFI" in p.part_type].pop()
        except IndexError:
            return Partition()

    def __str__(self) -> str:
        """
        Disk str formatting
        """
        return "\n".join([str(p) for p in self.partitions])


def to_iec(size: int) -> str:
    """
    The method to convert a size in iec format.
    """
    return re.sub('\\s', '', os.popen(f'printf "{size}" | numfmt --to=iec').read())


def from_iec(size: str) -> int:
    """
    The method to convert an iec formatted size in bytes.
    """
    return int(re.sub('\\s', '', os.popen(f'printf "{size}" | numfmt --from=iec').read()))


if __name__ == '__main__':
    disk = Disk('/dev/sdb')
    print(disk)
