#!/usr/bin/env python3
"""
    Main application class file
"""


import logging
from pathlib import Path
from pprint import pp

import numpy as np
from . import devices
import yaml

class codegen:
    """
        Main application class
    """
    def __init__(self) -> None:
        pass


    def load_config_yaml(self, config_path: Path):
        """
            Load config defines from YAML format
        """

        with open(config_path, "r") as stream:
            config = yaml.safe_load(stream)
            self.devices = config['devices']

    def device_short_id(self, id):
        return id[-4:]


    def run(self):
        """
            Primary execute function
        """

        device_registry = devices.DEVICES()

        # Step 1: find and validate devices ID and apply common values
        # map item property 'type' with proper value from DEVICES array

        for k, v in enumerate(self.devices):
            type = v['type']
            # Find device config from DEVICES object
            type_config = device_registry.get_from_id(id=type)
            # Update current item config from text ID to real array from device
            self.devices[k]['type'] = type_config

        logging.info("Processing %d devices", len(self.devices))

        # Step 2: Generate some common values for devices list
        # This will prepare devices with some common properties set

        self.item_ids = []
        self.zigbee_ids = []
        self.zigbee_devices_list = {}
        for x, item in enumerate(self.devices):
            # Ensure that device ID is unqique -> throw an error else
            if item['id'] in self.item_ids:
                raise Exception(f"Device ID {item['id']} is not unique!")
            self.item_ids.append(item['id'])
            self.devices[x]['mqtt_topic'] = f"{self.devices[x]['id']}"
            if np.in1d(['zigbee'], item['type']['types']).any():
                # Add to all Zigbee items generated MQTT topic like "zigbee-XXXX"
                self.devices[x]['zigbee_short'] = self.device_short_id(
                    item['zigbee_id'])
                # Add ids to check conflicts
                if self.devices[x]['zigbee_short'] in self.zigbee_ids:
                    raise Exception(f"Device ID {item['id']} is not unique!")
                self.zigbee_ids.append(self.devices[x]['zigbee_short'])
                self.zigbee_devices_list[item['zigbee_id']] = item['id']

        pp(self.devices)
        pp(self.zigbee_devices_list)


