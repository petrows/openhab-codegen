from pydoc_data.topics import topics
from typing import List
import numpy as np
from codegen.item import Item, MQTT_Item
from codegen.thing import *


class Device:
    """
        Represents device record from config
    """

    def __init__(self, config_device, config_type) -> None:
        self.type = config_type
        self.tags = config_type['types'] # Device 'tags'
        self.channels = config_device.get('channels', list())

        # Device ID
        # Simple: just use ID
        if 'id' in config_device:
            self.id = config_device['id']
        # Channel-driven: use from channel? Use first
        elif len(self.channels):
            self.id = list(self.channels.values())[0]['id']
        else:
            raise RuntimeError("Item %s: cant find ID", config_device)

        # Device Name
        # Simple: just use Name
        if 'name' in config_device:
            self.name = config_device['name']
        # Channel-driven: use from channel? Use first
        elif len(self.channels):
            self.name = list(self.channels.values())[0]['name']
        else:
            raise RuntimeError("Item %s: cant find Name", config_device)


        # Zigbee only: Zigbee address
        self.zigbee_id = config_device.get('zigbee_id', None)

    def set_global_config(self, config_global):
        """
            Set global options (like broker address, settings, etc)
        """
        self.config = config_global

    def get_device_address(self):
        # Zigbee: return device address
        if np.in1d(['zigbee'], self.type['types']).any():
            return self.zigbee_id
        # Others: return device ID
        return self.id

    def get_device_address_short(self):
        # Zigbee: return device address
        if np.in1d(['zigbee'], self.type['types']).any():
            return self.zigbee_id[-4:]
        # Others: return device ID
        return self.id

    def get_label(self) -> str:
        return f"{self.name} ({self.get_device_address()})"

    def get_comment(self) -> List[str]:
        conf_str = []
        conf_str.append(f"// {self.get_label()}")
        conf_str.append(
            f"// {self.type['device_name']}"
            f" / {self.type['device_url']}"
        )
        return conf_str

    def get_groups(self, type: Str) -> List[Str]:
        return list()

    def get_channel_groups(self, channel: Str, type: Str) -> List[Str]:
        return list()

    def is_tasmota(self) -> bool:
        return np.in1d(['tasmota'], self.tags).any()

    def has_monitoring(self) -> bool:
        return np.in1d(['activity'], self.tags).any()

    def has_tag(self, tag: Str) -> bool:
        return tag in self.tags

    def get_things(self) -> List[Thing]:
        """
            Prepare list of Things
        """

        things = list()

        # Generate items list for Tasmota devices
        if self.is_tasmota():
            things.extend(self.get_things_tasmota())

        return things

    def get_things_tasmota(self) -> List[Thing]:
        """
            Things for Tasmota.
            It has MQTT driven items, generate thing from this device
        """

        channels = []

        state_topic = f"tele/{self.get_device_address()}/STATE"
        result_topic = f"stat/{self.get_device_address()}/RESULT"

        # All tasmota reports some standart channels (WiFi signal, etc)

        # WiFi signal values
        channels.append(MQTT_ThingChannel(
            type='number',
            id='rssi',
            args={
                'stateTopic': state_topic,
                'transformationPattern': "JSONPATH:$.Wifi.RSSI",
            },
        ))
        channels.append(MQTT_ThingChannel(
            type='number',
            id='bssid',
            args={
                'stateTopic': state_topic,
                'transformationPattern': "JSONPATH:$.Wifi.BSSId",
            },
        ))
        # Load average
        channels.append(MQTT_ThingChannel(
            type='number',
            id='la',
            args={
                'stateTopic': state_topic,
                'transformationPattern': "JSONPATH:$.LoadAvg",
            },
        ))
        # Monitoring?
        if self.has_monitoring():
            channels.append(MQTT_ThingChannel(
                type='datetime',
                id='activity',
                args={
                    'stateTopic': state_topic,
                    'transformationPattern': "JS:z2m-activity.js",
                },
            ))

        # Enumerate device-specific channels

        for channel in self.type['tasmota_channels']:
            channel_args = {
                'stateTopic': result_topic,
                'transformationPattern': f"JSONPATH:$.{channel['id']}",
                'commandTopic': f"cmnd/{self.get_device_address()}/{channel['id']}",
            }
            if 'switch' == channel['type']:
                channel_args['on'] = "ON"
                channel_args['off'] = "OFF"
            if 'dimmer' == channel['type']:
                channel_args['min'] = "1"
                channel_args['max'] = "100"
            channels.append(MQTT_ThingChannel(
                type=channel['type'],
                id=channel['id'],
                args=channel_args,
            ))

        # Get Thing

        thing = MQTT_Thing(
            id=self.get_device_address(),
            name=self.name,
            broker=self.config['mqtt_broker_id'],
            channels=channels,
        )

        return [thing]

    def get_items(self) -> List[Item]:
        """
            Prepare list of Items
        """

        items: List[Item] = list()

        # Generate items list for Tasmota devices
        if self.is_tasmota():
            items.extend(self.get_items_tasmota())

        # Common items for devices

        # WIFI items
        if self.has_tag('rssi'):
            items.append(
                MQTT_Item(
                    id=f"{self.id}_rssi",
                    name=f"{self.name} RSSI [%.0f]",
                    type='Number:Dimensionless',
                    icon='network',
                    groups=self.get_groups(type='rssi'),
                    broker=self.config['mqtt_broker_id'],
                    channel_id='rssi',
                    sitemap_type='Text',
                )
            )
        if self.has_tag('bssid'):
            items.append(
                MQTT_Item(
                    id=f"{self.id}_bssid",
                    name=f"{self.name} BSSID [%s]",
                    type='String',
                    icon='network',
                    groups=self.get_groups(type='bssid'),
                    broker=self.config['mqtt_broker_id'],
                    channel_id='bssid',
                    sitemap_type='Text',
                )
            )

        return items

    def get_items_tasmota(self) -> List[Item]:
        """
            Things for Tasmota.
            It has MQTT driven items, generate thing from this device
        """

        items = list()

        for channel in self.type['tasmota_channels']:
            # Check device channels - has defined config in end-device?
            if channel['id'] in self.channels:
                channel_cfg = self.channels[channel['id']]
                items.append(
                    MQTT_Item(
                        id=f"{channel_cfg['id']}_sw",
                        name=channel_cfg['name'],
                        type='Switch',
                        groups=self.get_channel_groups(channel=channel['id'], type='sw'),
                        broker=self.config['mqtt_broker_id'],
                        channel_id=channel['id'],
                        sitemap_type='Switch',
                    )
                )

        return items
