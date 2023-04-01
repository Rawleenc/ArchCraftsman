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
The config related methods module
"""


import json
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.bundles.utils import get_bundle_type_by_name

from archcraftsman.globalinfo import GlobalInfo
from archcraftsman.partition import Partition
from archcraftsman.partitioninginfo import PartitioningInfo
from archcraftsman.prelaunchinfo import PreLaunchInfo
from archcraftsman.systeminfo import SystemInfo


def dict_to_obj(dict_obj, class_type):
    """
    Convert a dict to an object of a specific class.
    """
    obj = class_type()
    for key, value in dict_obj.items():
        if isinstance(value, dict):
            value = dict_to_obj(value, class_type)
        setattr(obj, key, value)
    return obj


def dict_to_bundle(dict_obj) -> Bundle:
    """
    Convert a dict to a bundle object.
    """
    bundle = get_bundle_type_by_name(dict_obj["name"])(
        dict_obj["name"], dict_obj["bundle_type"]
    )
    for key, value in dict_obj.items():
        setattr(bundle, key, value)
    return bundle


def dict_to_partition(dict_obj) -> Partition:
    """
    Convert a dict to a partition object.
    """
    partition = Partition()
    for key, value in dict_obj.items():
        setattr(partition, key, value)
    return partition


def deserialize(file_path: str):
    """
    Deserialize a json config file.
    """
    if not file_path:
        raise ValueError("Config file path is empty.")
    if not file_path.endswith(".json"):
        raise ValueError(f"{file_path} is not a json file.")
    with open(file_path, "r", encoding="UTF-8") as file:
        data = json.loads(file.read())
        global_info = GlobalInfo()
        global_info.pre_launch_info = dict_to_obj(
            data["pre_launch_info"], PreLaunchInfo
        )

        global_info.partitioning_info = dict_to_obj(
            data["partitioning_info"], PartitioningInfo
        )
        global_info.partitioning_info.partitions = []
        for bundle in data["partitioning_info"]["partitions"]:
            global_info.partitioning_info.partitions.append(dict_to_partition(bundle))

        global_info.system_info = dict_to_obj(data["system_info"], SystemInfo)
        global_info.system_info.bundles = []
        for bundle in data["system_info"]["bundles"]:
            global_info.system_info.bundles.append(dict_to_bundle(bundle))
