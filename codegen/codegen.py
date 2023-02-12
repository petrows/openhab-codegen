#!/usr/bin/env python3
"""
    Main application class file
"""


from difflib import context_diff, ndiff, unified_diff
import logging
from pathlib import Path
from pprint import pp
import sys
from typing import List

import numpy as np
from codegen import thing
from codegen.device import Device

from codegen.thing import Thing
from . import devices
import yaml

PREAMBULA = """
// ==========================================
// THIS FILE IS AUTO GENERATED
// Do not edit by hands
// Use this command to regenerate:
// python3 ./bin/codegen.py
// ==========================================

""".split('\n')

class codegen:
    """
        Main application class
    """

    config_defaults = {
        "mqtt_broker_id": "openhab",
        # Use deivce ID as topic for Zegbee
        "zibee_pretty_name_topic": True,
    }

    def __init__(
            self,
            write=False,
            openhab_path:Path=None,
        ) -> None:
        self.write = write
        self.self_path = Path(__file__).parent.parent
        self.openhab_path = openhab_path
        self.devices:List[Device] = list()
        pass


    def load_config_yaml(self, config_path: Path):
        """
            Load config defines from YAML format
        """

        with open(config_path, "r") as stream:
            config = yaml.safe_load(stream)
            self.config = self.config_defaults | config['config']
            self.config_devices = config['devices']

    def write_file(self, data, file=Path):
        # Join data file to strings + trailing \n
        things_conf = '\n'.join(data) + '\n'
        # We have previos version?
        things_conf_old = list()
        try:
            with open(file, 'r') as f:
                things_conf_old = f.readlines()
        except:
            pass
        # Disaply diff
        if things_conf_old:
            sys.stdout.writelines(
                unified_diff(
                    things_conf_old,
                    # Emulate data read by readlines()
                    [s + "\n" for s in data],
                    fromfile=file.name,
                    tofile=file.name,
                )
            )
        # Create directory
        file.parent.mkdir(parents=True, exist_ok=True)
        # Write file...
        if self.write:
            with open(file, 'w') as f:
                f.write(things_conf)


    def update_things(self, file=Path):

        # Generate THINGS
        conf_str: List[str] = list()
        conf_str.extend(PREAMBULA)
        for device in self.devices:
            things = device.get_things()

            conf_str.extend(device.get_comment())
            for thing in things:
                conf_str.extend(thing.get_config())

            logging.debug("Device: %s", device.get_label())

        self.write_file(conf_str, file)

    def update_items(self, file=Path):

        # Generate ITEMS
        conf_str: List[str] = list()
        conf_str.extend(PREAMBULA)
        for device in self.devices:
            items = device.get_items()

            conf_str.extend(device.get_comment())
            for item in items:
                conf_str.extend(item.get_config())

        self.write_file(conf_str, file)

    def update_transform(self, dir=Path):
        transform_src = Path(self.self_path / "transform")
        transform_files = transform_src.iterdir()

        dir.mkdir(parents=True, exist_ok=True)

        for f in transform_files:
            self.write_file(open(f).read().splitlines(), dir / f.name)

    def update_rules(self, file=Path):
        # Generate rules list
        conf_str: List[str] = list()
        conf_str.extend(PREAMBULA)
        for device in self.devices:
            conf_str.extend(device.get_rules_header())
        conf_str.extend(['// ----------------------------'])
        for device in self.devices:
            conf_str.extend(device.get_rules())

        self.write_file(conf_str, file)

    def update_gen_sitemap(self, file=Path):
        # Generate rules list
        conf_str: List[str] = list()
        conf_str.extend(PREAMBULA)
        conf_str.extend(['sitemap gen label="GEN ITEMS"','{'])

        for device in self.devices:
            conf_str.extend([f'Frame label="{device.get_label()}" {{'])
            items = device.get_items()
            conf_str.extend(device.get_comment())
            for item in items:
                conf_str.extend(item.get_sitemap_config())
            conf_str.extend(['}'])

        conf_str.extend(['}'])

        self.write_file(conf_str, file)


    def run(self):
        """
            Primary execute function
        """

        device_registry = devices.DEVICES()

        # Step 1: find and validate devices ID and apply common values
        # map item property 'type' with proper value from DEVICES array

        self.item_addresses = []

        for device in self.config_devices:
            device_obj = device_registry.get_device(device, self.config)
            device_addr = device_obj.get_device_address()
            self.devices.append(device_obj)
            if device_addr in self.item_addresses:
                raise Exception(f"Device Address {device_addr} is not unique!")
            self.item_addresses.append(device_addr)

        logging.info("Processing %d devices", len(self.devices))

        self.update_things(
            file=self.openhab_path / "things" / "gen_things.things",
        )

        self.update_items(
            file=self.openhab_path / "items" / "gen_items.items",
        )

        self.update_rules(
            file=self.openhab_path / "rules" / "gen_auto.rules",
        )

        self.update_gen_sitemap(
            file=self.openhab_path / "sitemaps" / "gen.sitemap",
        )

        self.update_transform(
            dir=self.openhab_path / "transform",
        )


