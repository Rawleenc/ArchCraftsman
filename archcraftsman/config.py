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
import os
import sys

from archcraftsman import info
from archcraftsman.arguments import shell, test
from archcraftsman.base import print_error, print_step, print_sub_step
from archcraftsman.bundles.bundle import Bundle
from archcraftsman.bundles.utils import get_bundle_type_by_name
from archcraftsman.partition import Partition
from archcraftsman.partitioninginfo import PartitioningInfo
from archcraftsman.prelaunchinfo import PreLaunchInfo
from archcraftsman.systeminfo import SystemInfo


def serialize():
    """
    Serialize the GlobalInfo object to a json file.
    """
    json_str = json.dumps(info, default=lambda o: o.__dict__, sort_keys=True, indent=2)
    file_path = (
        f"/mnt/home/{info.ai.system_info.user_name}/{info.ai.system_info.hostname}.json"
        if info.ai.system_info.user_name
        else f"/mnt/root/{info.ai.system_info.hostname}.json"
    )
    file_path = (
        file_path
        if not test() and not shell()
        else f"{info.ai.system_info.hostname}.json"
    )
    if os.path.exists(file_path):
        with open(file_path, "w", encoding="UTF-8") as file:
            file.write(json_str)


def dict_to_obj(dict_obj, class_type):
    """
    Convert a dict to an object of a specific class.
    """
    obj = class_type()
    for key, value in dict_obj.items():
        if isinstance(value, dict):
            value = dict_to_obj(value, class_type)
        if hasattr(obj, key):
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
        if hasattr(bundle, key):
            setattr(bundle, key, value)
    return bundle


def dict_to_partition(dict_obj) -> Partition:
    """
    Convert a dict to a partition object.
    """
    partition = Partition()
    for key, value in dict_obj.items():
        if hasattr(partition, key):
            setattr(partition, key, value)
    return partition


def validate(data: dict, model_object):
    """
    Validate a config file.
    """
    for key, value in data.items():
        print_sub_step(f"Validating {key}...")
        if not hasattr(model_object, key):
            print_error(f"{key} is not a valid key.", do_pause=False)
            sys.exit(1)
        model_value = getattr(model_object, key)
        if isinstance(value, dict):
            validate(value, model_value)
            continue
        if isinstance(value, list) and len(model_value) > 0:
            for i, item in enumerate(value):
                if isinstance(item, dict):
                    validate(item, model_value[i])
            continue
        model_value_type = type(model_value)
        if not isinstance(value, model_value_type) and not issubclass(
            model_value_type, type(value)
        ):
            print_error(
                f"{key} is not a valid key. {key} should be {model_value_type}",
                do_pause=False,
            )
            sys.exit(1)


def deserialize(file_path: str):
    """
    Deserialize a json config file.
    """
    if not file_path:
        print_error("Config file path is empty.")
        sys.exit(1)
    if not file_path.endswith(".json"):
        print_error(f"{file_path} is not a json file.")
        sys.exit(1)
    print_step("Deserializing config file...", clear=False)
    with open(file_path, "r", encoding="UTF-8") as file:
        data = json.loads(file.read())
        info.ai.pre_launch_info = dict_to_obj(data["pre_launch_info"], PreLaunchInfo)

        info.ai.partitioning_info = dict_to_obj(
            data["partitioning_info"], PartitioningInfo
        )
        info.ai.partitioning_info.partitions = []
        for bundle in data["partitioning_info"]["partitions"]:
            info.ai.partitioning_info.partitions.append(dict_to_partition(bundle))

        info.ai.system_info = dict_to_obj(data["system_info"], SystemInfo)
        info.ai.system_info.bundles = []
        for bundle in data["system_info"]["bundles"]:
            info.ai.system_info.bundles.append(dict_to_bundle(bundle))
    print_step("Validating config file...", clear=False)
    validate(data, info.AllInfo())
