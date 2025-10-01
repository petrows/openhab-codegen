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
        # Default topic for MQTT
        "mqtt_topic": "zigbee2mqtt",
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
        self.configs = list()
        pass

    def load_config_yaml(self, config_path: Path):
        """
            Load config defines from YAML format
            from <path>/conf/*.yaml
        """
        self.config_path = config_path
        confgis_list = config_path.glob('conf/*.yaml')
        for config_file in confgis_list:
            with open(config_file, "r") as stream:
                logging.info("Reading config from %s", str(config_file))
                config_yaml = yaml.safe_load(stream)
                config_obj = {
                    'id': config_file.stem,
                    'file': config_file,
                    'config': self.config_defaults | config_yaml['config'],
                    'devices': config_yaml.get('devices', []),
                    'devices_obj': list(),
                }
                self.configs.append(config_obj)
        with open(config_path / 'y2m.yaml', "r") as stream:
            config_yaml = yaml.safe_load(stream)
            self.config_y2m = config_yaml.get('y2m', {'rooms':{}})

    def write_file(self, data, file=Path):
        # Join data file to strings + trailing \n
        things_conf = '\n'.join(data) + '\n'
        # We have previos version?
        things_conf_old = list()
        try:
            with open(file, 'r') as f:
                things_conf_old = f.readlines()
        except:
            logging.info("File %s does not exist, will be created", str(file))
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
        for config in self.configs:
            for device in config['devices_obj']:
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
        for config in self.configs:
            for device in config['devices_obj']:
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
        for config in self.configs:
            for device in config['devices_obj']:
                conf_str.extend(device.get_rules_header())
        conf_str.extend(['// ----------------------------'])
        for config in self.configs:
            for device in config['devices_obj']:
                conf_str.extend(device.get_rules())

        self.write_file(conf_str, file)

    def update_gen_sitemap(self, file=Path):
        # Generate rules list
        conf_str: List[str] = list()
        conf_str.extend(PREAMBULA)
        conf_str.extend(['sitemap gen label="GEN ITEMS"','{'])

        for config in self.configs:
            conf_str.extend([f'Text label="Z2M {config["id"]}" {{'])
            for device in config['devices_obj']:
                conf_str.extend([f'Frame label="{device.get_label()}" {{'])
                items = device.get_items()
                conf_str.extend(device.get_comment())
                for item in items:
                    conf_str.extend(item.get_sitemap_config())
                conf_str.extend(['}'])
            conf_str.extend(['}'])

        conf_str.extend(['}'])

        self.write_file(conf_str, file)

    def update_devices_yaml(self, dir=Path):
        # Generate devices.yaml (per-instance)
        for config in self.configs:
            z2m_devices_conf = {}
            for device in config['devices_obj']:
                if device.is_zigbee():
                    device_conf = {}
                    device_conf['friendly_name'] = device.get_id()
                    device_conf = device_conf | device.get_zigbee_device_config()
                    z2m_devices_conf[device.get_device_address()] = device_conf
            self.write_file(yaml.dump(z2m_devices_conf).splitlines(), dir / f"{config['id']}.yaml")

    def update_y2m_js(self, file=Path):
        # Generate yandex2mqtt
        # This config is optional
        if not self.config_y2m:
            return
        # Copy template
        tpl_src = Path(self.self_path / "y2m/yandex2mqtt.template.js")
        self.write_file(open(tpl_src).read().splitlines(), file.parent / "yandex2mqtt.template.js")
        rooms = self.config_y2m['rooms']

        conf_str: List[str] = list()
        # Include template
        conf_str.append('const tpl = require("./yandex2mqtt.template")')
        conf_str.append('const { LIGHT, LightGroup, Light, Thermostat, SensorClimate, SensorWindow, Shutter } = tpl')
        conf_str.append('const ROOMS = {')
        for room_id, room in rooms.items():
            conf_str.append(f'  {room_id}: \'{room}\',')
        conf_str.append('}')
        conf_str.append('module.exports = {')
        conf_str.append('devices: [')
        for config in self.configs:
            for device in config['devices_obj']:
                if device.has_y2m():
                    conf_str.extend(device.get_y2m_config())
        conf_str.append(']')
        conf_str.append('}')
        self.write_file(conf_str, file)

    def run(self):
        """
            Primary execute function
        """

        device_registry = devices.DEVICES()

        # Step 1: find and validate devices ID and apply common values
        # map item property 'type' with proper value from DEVICES array

        self.item_addresses = []
        self.item_ids = []

        for config in self.configs:
            for device in config['devices']:
                device_obj = device_registry.get_device(device, config['config'])
                device_addr = device_obj.get_device_address()
                device_id = device_obj.get_id()
                config['devices_obj'].append(device_obj)
                if device_addr in self.item_addresses:
                    raise Exception(f"Device Address {device_addr} is not unique!")
                self.item_addresses.append(device_addr)
                if device_id in self.item_ids:
                    raise Exception(f"Device ID {device_id} is not unique!")
                self.item_ids.append(device_id)

            logging.info("Processing %d devices for %s", len(config['devices_obj']), config['id'])

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

        # One file per-instance
        self.update_devices_yaml(
            dir=self.config_path / "devices/",
        )

        self.update_y2m_js(
            file=self.openhab_path / "yandex2mqtt.codegen.js",
        )
