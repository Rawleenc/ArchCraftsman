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
The global information singleton module
"""
import json
from threading import Lock
from archcraftsman.globalargs import GlobalArgs

from archcraftsman.prelaunchinfo import PreLaunchInfo
from archcraftsman.partitioninginfo import PartitioningInfo
from archcraftsman.systeminfo import SystemInfo


class GlobalInfoMeta(type):
    """
    Thread-safe implementation of Singleton to manage translations.
    """

    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class GlobalInfo(metaclass=GlobalInfoMeta):
    """
    The singleton implementation containing the translation method to use.
    """

    def __init__(self) -> None:
        self.pre_launch_info: PreLaunchInfo = PreLaunchInfo()
        self.partitioning_info: PartitioningInfo = PartitioningInfo()
        self.system_info: SystemInfo = SystemInfo()

    def serialize(self):
        """
        Serialize the GlobalInfo object to a json file.
        """
        json_str = json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, indent=2
        )
        file_path = (
            f"/mnt/home/{self.system_info.user_name}/{self.system_info.hostname}.json"
            if self.system_info.user_name
            else f"/mnt/root/{self.system_info.hostname}.json"
        )
        file_path = (
            file_path
            if not GlobalArgs().test()
            else f"{self.system_info.hostname}.json"
        )
        with open(file_path, "w", encoding="UTF-8") as file:
            file.write(json_str)
