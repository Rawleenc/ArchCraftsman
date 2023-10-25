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

import archcraftsman.arguments
import archcraftsman.base
import archcraftsman.bundles.bundle
import archcraftsman.bundles.utils
import archcraftsman.info
import archcraftsman.partition
import archcraftsman.partitioninginfo
import archcraftsman.prelaunchinfo
import archcraftsman.systeminfo


def serialize():
    """
    Serialize the GlobalInfo object to a json file.
    """
    json_str = json.dumps(
        archcraftsman.info.ai,
        default=lambda o: {
            k: v for (k, v) in o.__dict__.items() if not k.startswith("_")
        },
        sort_keys=True,
        indent=2,
    )
    file_path = (
        f"/mnt/home/{archcraftsman.info.ai.system_info.user_name}/{archcraftsman.info.ai.system_info.hostname}.json"
        if archcraftsman.info.ai.system_info.user_name
        else f"/mnt/root/{archcraftsman.info.ai.system_info.hostname}.json"
    )
    file_path = (
        file_path
        if not archcraftsman.arguments.test() and not archcraftsman.arguments.shell()
        else f"{archcraftsman.info.ai.system_info.hostname}.json"
    )
    if os.path.exists(file_path):
        os.remove(file_path)
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


def dict_to_bundle(dict_obj) -> archcraftsman.bundles.bundle.Bundle:
    """
    Convert a dict to a bundle object.
    """
    bundle = archcraftsman.bundles.utils.get_bundle_type_by_name(dict_obj["name"])(
        dict_obj["name"]
    )
    for key, value in dict_obj.items():
        if hasattr(bundle, key):
            setattr(bundle, key, value)
    return bundle


def dict_to_partition(dict_obj) -> archcraftsman.partition.Partition:
    """
    Convert a dict to a partition object.
    """
    partition = archcraftsman.partition.Partition()
    for key, value in dict_obj.items():
        if hasattr(partition, key):
            setattr(partition, key, value)
    return partition


def validate(data: dict, model_object):
    """
    Validate a config file.
    """
    for key, value in data.items():
        archcraftsman.base.print_sub_step(f"Validating {key}...")
        if not hasattr(model_object, key):
            archcraftsman.base.print_error(f"{key} is not a valid key.", do_pause=False)
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
            archcraftsman.base.print_error(
                f"{key} is not a valid key. {key} should be {model_value_type}",
                do_pause=False,
            )
            sys.exit(1)


def deserialize(file_path: str):
    """
    Deserialize a json config file.
    """
    if not file_path:
        archcraftsman.base.print_error("Config file path is empty.")
        sys.exit(1)
    if not file_path.endswith(".json"):
        archcraftsman.base.print_error(f"{file_path} is not a json file.")
        sys.exit(1)
    archcraftsman.base.print_step("Deserializing config file...", clear=False)
    with open(file_path, "r", encoding="UTF-8") as file:
        data = json.loads(file.read())
        archcraftsman.info.ai.pre_launch_info = dict_to_obj(
            data["pre_launch_info"], archcraftsman.prelaunchinfo.PreLaunchInfo
        )

        archcraftsman.info.ai.partitioning_info = dict_to_obj(
            data["partitioning_info"], archcraftsman.partitioninginfo.PartitioningInfo
        )
        archcraftsman.info.ai.partitioning_info.partitions = []
        for bundle in data["partitioning_info"]["partitions"]:
            archcraftsman.info.ai.partitioning_info.partitions.append(
                dict_to_partition(bundle)
            )

        archcraftsman.info.ai.system_info = dict_to_obj(
            data["system_info"], archcraftsman.systeminfo.SystemInfo
        )
        archcraftsman.info.ai.system_info.bundles = []
        for bundle in data["system_info"]["bundles"]:
            archcraftsman.info.ai.system_info.bundles.append(dict_to_bundle(bundle))
    archcraftsman.base.print_step("Validating config file...", clear=False)
    fake = archcraftsman.info.AllInfo()
    for partition in archcraftsman.info.ai.partitioning_info.partitions:
        fake.partitioning_info.partitions.append(type(partition)())
    for bundle in archcraftsman.info.ai.system_info.bundles:
        fake.system_info.bundles.append(type(bundle)())
    validate(data, fake)
