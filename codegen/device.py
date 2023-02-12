from pydoc_data.topics import topics
from typing import List
import numpy as np
from codegen.item import Item, MQTT_Item
from codegen.thing import *
from pprint import pprint
import json

class Device:
    """
        Represents device record from config
    """

    def __init__(self, config_device, config_type) -> None:
        self.type = config_type
        self.tags = config_type['types'] # Device 'tags'
        self.channels = config_device.get('channels', {})
        self.expire = config_device.get('expire', None)
        self.icon = config_device.get('icon', None)

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

    def get_expire(self, command='OFF') -> str:
        return f'{self.expire},command={command}'

    def get_channel_expire(self, channel: str, command='OFF') -> str:
        if channel in self.channels and 'expire' in self.channels[channel]:
            return f'{self.channels[channel]["expire"]},command={command}'
        return None

    def get_groups(self, type: str) -> List[str]:
        return list()

    def get_channel_groups(self, channel: str, type: str) -> List[str]:
        return list()

    def get_icon(self, default='light') -> str:
        if self.icon:
            return self.icon
        return default

    def is_tasmota(self) -> bool:
        return np.in1d(['tasmota'], self.tags).any()

    def is_zigbee(self) -> bool:
        return np.in1d(['zigbee'], self.tags).any()

    def has_monitoring(self) -> bool:
        return np.in1d(['activity'], self.tags).any()

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def has_tag_any(self, *tags) -> bool:
        return np.in1d(tags, self.tags).any()

    def get_things(self) -> List[Thing]:
        """
            Prepare list of Things
        """

        things = list()

        # Generate items list for Tasmota devices
        if self.is_tasmota():
            things.extend(self.get_things_tasmota())

        # Generate items list for Zigbee devices
        if self.is_zigbee():
            things.extend(self.get_things_zigbee())

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

    def get_things_zigbee(self) -> List[Thing]:
        """
            Things for Zigbee.
            It has MQTT driven items, generate thing from this device
        """

        channels = []

        command_topic = f"zigbee2mqtt/{self.id}/set"
        state_topic = f"zigbee2mqtt/{self.id}"

        # Device has switch (Lamp, Wall socket)
        if self.has_tag_any('lamp', 'plug'):
            channels.append(MQTT_ThingChannel(
                type='switch',
                id='state',
                args={
                    'stateTopic': state_topic,
                    'commandTopic': command_topic,
                    'transformationPattern': 'JSONPATH:$.state',
                    'formatBeforePublish': json.dumps({'state': "%s", 'transition': 1}),
                },
            ))
        # Device has switch (multi-gang) option
        if self.has_tag('plug_mt'):
            for channel_id, _ in self.channels.items():
                channels.append(MQTT_ThingChannel(
                    type='switch',
                    id=f'state_{channel_id}',
                    args={
                        'stateTopic': state_topic,
                        'commandTopic': command_topic,
                        'transformationPattern': f'JSONPATH:$.state_{channel_id}',
                        'formatBeforePublish': json.dumps({f'state_{channel_id}': "%s"})
                    },
                ))
        # Lamps have dimmer
        if self.has_tag('lamp'):
            channels.append(MQTT_ThingChannel(
                type='dimmer',
                id='dim',
                args={
                    'stateTopic': state_topic,
                    'commandTopic': command_topic,
                    'transformationPattern': 'JSONPATH:$.brightness',
                    'formatBeforePublish': json.dumps({'brightness': "%d", 'transition': 3}),
                    'min': 1,
                    'max': 255,
                },
            ))
        # Lamps have color temp?
        if self.has_tag('ct'):
            channels.append(MQTT_ThingChannel(
                type='dimmer',
                id='ct',
                args={
                    'stateTopic': state_topic,
                    'commandTopic': command_topic,
                    'transformationPattern': 'JSONPATH:$.color_temp',
                    'formatBeforePublish': json.dumps({'color_temp': "%d", 'transition': 3}),
                    'min': 150,
                    'max': 500,
                },
            ))
        # Device is remote
        if self.has_tag('remote'):
            channels.append(MQTT_ThingChannel(
                type='string',
                id='action',
                args={
                    'stateTopic': state_topic,
                    'commandTopic': command_topic,
                    'transformationPattern': 'JSONPATH:$.action',
                    'trugger': 'true'
                },
            ))

        # Get Thing

        thing = MQTT_Thing(
            id=self.id,
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

        # Generate items list for Zigbee devices
        if self.is_zigbee():
            items.extend(self.get_items_zigbee())

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

        # Common devices

        # Device has switch (Lamp, Wall socket)
        if self.has_tag_any('lamp', 'plug'):
            items.append(
                MQTT_Item(
                    id=f"{self.id}_sw",
                    name=self.name,
                    type='Switch',
                    icon=self.get_icon(default='light'),
                    groups=self.get_groups(type='sw'),
                    expire=self.get_expire(),
                    broker=self.config['mqtt_broker_id'],
                    channel_id=f'{self.id}:state',
                    sitemap_type='Switch',
                )
            )
        # Multi-gang switch
        if self.has_tag('plug_mt'):
            for channel_id, channel in self.channels.items():
                items.append(
                    MQTT_Item(
                        id=f'{channel["id"]}_sw',
                        name=channel["name"],
                        type='Switch',
                        icon=self.get_icon(default='light'),
                        groups=self.get_channel_groups(
                            channel=channel_id, type='sw'),
                        expire=self.get_channel_expire(channel=channel_id),
                        broker=self.config['mqtt_broker_id'],
                        channel_id=f'{self.id}:state_{channel_id}',
                        sitemap_type='Switch',
                    )
                )

        # Simple information channes, read only
        simple_channels = [
            {'id': 'temperature', 'title': 'temp  [%.0f %unit%]', 'type': 'Number:Temperature' },
            {'id': 'humidity', 'title': 'humidity  [%.0f %unit%]', 'type': 'Number:Dimensionless' },
            {'id': 'pressure', 'title': 'pressure  [%.0f %unit%]', 'type': 'Number:Pressure' },
            {'id': 'leak', 'title': '[%s]', 'type': 'Switch', 'icon': 'flow' },
            {'id': 'contact', 'title': '[%s]', 'type': 'Contact', 'icon': 'door' },
            {'id': 'position', 'title': 'POS [%.0f %%]', 'type': 'Number:Dimensionless', 'icon': 'heating' },
        ]
        for metric in simple_channels:
            if self.has_tag(metric['id']):
                if 'icon' not in metric:
                    metric['icon'] = metric['id']
                items.append(
                    MQTT_Item(
                        id=f'{self.id}_{metric["id"]}',
                        name=f'{self.name} {metric["title"]}',
                        type=metric["type"],
                        icon=self.get_icon(default=metric["id"]),
                        groups=self.get_groups(type=metric["id"]),
                        broker=self.config['mqtt_broker_id'],
                        channel_id=f'{self.id}:{metric["id"]}',
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
                        icon=self.get_icon(default='light'),
                        groups=self.get_channel_groups(channel=channel['id'], type='sw'),
                        broker=self.config['mqtt_broker_id'],
                        channel_id=channel['id'],
                        sitemap_type='Switch',
                    )
                )

        return items

    def get_items_zigbee(self) -> List[Item]:
        """
            Things for Zigbee.
            It has MQTT driven items, generate thing from this device
        """

        items = list()

        # All zigbee lamps have dimmer
        if self.has_tag('lamp'):
            items.append(
                MQTT_Item(
                    id=f"{self.id}_dim",
                    name=f'{self.name} DIM [%d %%]',
                    type='Dimmer',
                    icon=self.get_icon(default='light'),
                    groups=self.get_groups(type='dim'),
                    broker=self.config['mqtt_broker_id'],
                    channel_id=f'{self.id}:dim',
                    sitemap_type='Slider',
                )
            )

        # Some zigbee lamps have ct
        if self.has_tag('ct'):
            items.append(
                MQTT_Item(
                    id=f"{self.id}_ct",
                    name=f'{self.name} CT [JS(display-mired.js): %s]',
                    type='Dimmer',
                    icon=self.get_icon(default='light'),
                    groups=self.get_groups(type='ct'),
                    broker=self.config['mqtt_broker_id'],
                    channel_id=f'{self.id}:ct',
                    sitemap_type='Slider',
                )
            )

        return items
