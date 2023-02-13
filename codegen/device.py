from pydoc_data.topics import topics
from typing import List
import numpy as np
from codegen.item import Item, MQTT_Item
from codegen.thing import *
from pprint import pprint
import json
import jinja2

# Simple information channes, read only (all devices)
DEVICE_SIMPLE_CHANNELS = [
    {'id': 'temperature', 'title': 'temp  [%.0f %unit%]', 'type': 'Number:Temperature', 'unit': 'C°' },
    {'id': 'local_temperature', 'title': 'temp  [%.0f %unit%]', 'type': 'Number:Temperature', 'unit': 'C°' },
    {'id': 'humidity', 'title': 'humidity  [%.0f %%]', 'type': 'Number:Dimensionless', 'unit': '%' },
    {'id': 'pressure', 'title': 'pressure  [%.0f %unit%]', 'type': 'Number:Pressure', 'unit': 'hPa' },
    {'id': 'leak', 'title': '[%s]', 'type': 'Switch', 'icon': 'flow', 'channel_args': {'on':'true','off':'false'} },
    {'id': 'contact', 'title': '[%s]', 'type': 'Contact', 'icon': 'door', 'channel_args': {'on':'false','off':'true'} },
    {'id': 'occupancy', 'title': '[%s]', 'type': 'Switch', 'icon': 'motion', 'channel_args': {'on':'true','off':'false'} },
    {'id': 'position', 'title': 'POS [%.0f %%]', 'type': 'Number:Dimensionless', 'icon': 'heating', 'unit': '%' },
    {'id': 'co2', 'title': 'CO₂ [%d %unit%]', 'type': 'Number:Dimensionless', 'icon': 'co2', 'unit': 'ppm' },
    {'id': 'co2_led', 'title': 'CO₂ alarm [%s]', 'type': 'Switch', 'icon': 'alarm'},
    {'id': 'battery', 'title': ' BAT [%d %%]', 'type': 'Number:Dimensionless', 'icon': 'battery', 'unit': '%'},
    {'id': 'battery_voltage', 'title': '[%.0f mV]', 'type': 'Number:ElectricPotential', 'icon': 'energy', 'unit': 'mV'},
]

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
        self.groups = config_device.get('groups', {})

        # If device needs rules, we will store it here
        self.rules_header = []
        self.rules = []

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

        # Custom device ID (for MQTT topic)
        if 'device_id' in config_device:
            self.device_id = config_device['device_id']

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

    def get_zigbee_device_config(self):
        """
            This function returns additional config for devices.yaml
        """
        cfg = {}
        if self.is_simulated_brightness():
            cfg['simulated_brightness'] = []
        return cfg

    def get_id(self) -> str:
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
        if self.expire:
            return f'{self.expire},command={command}'
        else:
            return None

    def get_channel_expire(self, channel: str, command='OFF') -> str:
        if channel in self.channels and 'expire' in self.channels[channel]:
            return f'{self.channels[channel]["expire"]},command={command}'
        return None

    def get_groups(self, type: str) -> List[str]:
        groups = ['g_all_' + type]
        if type in self.groups:
            groups.extend(self.groups[type])
        return groups

    def get_channel_groups(self, channel: str, type: str) -> List[str]:
        groups = ['g_all_' + type]
        if channel in self.groups:
            groups.extend(self.groups[channel])
        return groups

    def get_icon(self, default='light') -> str:
        if self.icon:
            return self.icon
        return default

    def get_name(self) -> str:
        return self.name

    def get_channel_type_from_item(self, item: dict) -> str:
        item_type = item['type']
        if 'Number' in item_type: return 'number'
        if 'Switch' in item_type: return 'switch'
        if 'Contact' in item_type: return 'contact'
        return 'string'

    def is_simulated_brightness(self) -> bool:
        simulated = False # Default is no
        if 'simulated_brightness' in self.config:
            return self.config['simulated_brightness']
        if 'simulated_brightness' in self.type:
            return self.type['simulated_brightness']
        return False

    def is_tasmota(self) -> bool:
        return np.in1d(['tasmota'], self.tags).any()

    def is_zigbee(self) -> bool:
        return np.in1d(['zigbee'], self.tags).any()

    def is_petrows(self) -> bool:
        return np.in1d(['petrows'], self.tags).any()

    def has_monitoring(self) -> bool:
        return np.in1d(['activity'], self.tags).any()

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags

    def has_tag_any(self, *tags) -> bool:
        return np.in1d(tags, self.tags).any()

    def get_rules(self) -> List[str]:
        return self.rules

    def get_rules_header(self) -> List[str]:
        return self.rules_header

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

        # Generate items list for DIY devices
        if self.is_petrows():
            things.extend(self.get_things_petrows())

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
            type='string',
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
                    'transformationPattern': "JS:codegen-activity.js",
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
                    'transformationPattern': 'REGEX:(.*"brightness".*)∩JSONPATH:$.brightness',
                    'transformationPatternOut': 'JS:codegen-cmd-brightness.js',
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
                    'transformationPattern': 'REGEX:(.*"color_temp".*)∩JSONPATH:$.color_temp',
                    'transformationPatternOut': 'JS:codegen-cmd-color_temp.js',
                    'min': 150,
                    'max': 500,
                },
            ))
        # Lamps have color?
        if self.has_tag('color'):
            channels.append(MQTT_ThingChannel(
                type='color',
                id='color',
                args={
                    'commandTopic': command_topic,
                    'transformationPatternOut': 'JS:codegen-cmd-color_xy.js',
                },
            ))
            channels.append(MQTT_ThingChannel(
                type='string',
                id='color_mode',
                args={
                    'stateTopic': state_topic,
                    'transformationPattern': 'REGEX:(.*"color_mode".*)∩JSONPATH:$.color_mode',
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
                    'transformationPattern': 'REGEX:(.*"action".*)∩JSONPATH:$.action',
                    'trigger': 'true'
                },
            ))
            # Simulate brightness?
            if self.is_simulated_brightness():
                channels.append(MQTT_ThingChannel(
                    type='dimmer',
                    id='dim',
                    args={
                        'stateTopic': state_topic,
                        'transformationPattern': 'REGEX:(.*"brightness".*)∩JSONPATH:$.brightness',
                        'min': 0,
                        'max': 255,
                    },
                ))
        # Device is TRV
        if self.has_tag('thermostat'):
            channels.append(MQTT_ThingChannel(
                type='number',
                id='thermostat',
                args={
                    'stateTopic': state_topic,
                    'commandTopic': command_topic,
                    'transformationPattern': 'REGEX:(.*"current_heating_setpoint".*)∩JSONPATH:$.current_heating_setpoint',
                    'transformationPatternOut': 'JS:codegen-cmd-thermostat-point.js',
                    'unit': 'C°',
                },
            ))
            channels.append(MQTT_ThingChannel(
                type='string',
                id='thermostat_mode',
                args={
                    'stateTopic': state_topic,
                    'commandTopic': command_topic,
                    'transformationPattern': 'REGEX:(.*"system_mode".*)∩JSONPATH:$.system_mode',
                    'formatBeforePublish': json.dumps({'system_mode': '%s'})
                },
            ))
            channels.append(MQTT_ThingChannel(
                type='switch',
                id='thermostat_enable',
                args={
                    'stateTopic': state_topic,
                    'commandTopic': command_topic,
                    'transformationPattern': 'REGEX:(.*"system_mode".*)∩JS:codegen-thermostat-enable.js',
                    'transformationPatternOut': 'JS:codegen-cmd-thermostat-enable.js',
                },
            ))

        for metric in DEVICE_SIMPLE_CHANNELS:
            if self.has_tag(metric['id']):
                args = {
                    'stateTopic': state_topic,
                    'transformationPattern': f'REGEX:(.*"{metric["id"]}".*)∩JSONPATH:$.{metric["id"]}',
                }
                if 'unit' in metric:
                    args['unit'] = metric['unit']
                if 'channel_args' in metric:
                    args = args | metric['channel_args']
                channels.append(MQTT_ThingChannel(
                    type=self.get_channel_type_from_item(metric),
                    id=metric['id'],
                    args=args,
                ))

        # Monitoring?
        if self.has_monitoring():
            channels.append(MQTT_ThingChannel(
                type='datetime',
                id='activity',
                args={
                    'stateTopic': state_topic,
                    'transformationPattern': "JS:codegen-activity.js",
                },
            ))

        # Battery control
        if self.has_tag('battery'):
            channels.append(MQTT_ThingChannel(
                type='switch',
                id='battery_low',
                args={
                    'stateTopic': state_topic,
                    'transformationPattern': 'REGEX:(.*"battery".*)∩JS:codegen-lowbat.js',
                },
            ))
        else:
            if self.has_tag('battery_low'):
                channels.append(MQTT_ThingChannel(
                    type='switch',
                    id='battery_low',
                    args={
                        'stateTopic': state_topic,
                        'transformationPattern': 'REGEX:(.*"battery_low".*)∩JSONPATH:$.battery_low',
                        'on': 'true',
                        'off': 'false',
                    },
                ))

        # If device reports battery voltage, we can decide
        if self.has_tag('battery_voltage'):
            batt_type = self.type['batt_type']
            channels.append(MQTT_ThingChannel(
                type='switch',
                id='battery_low',
                args={
                    'stateTopic': state_topic,
                    'transformationPattern': f'REGEX:(.*"battery".*)∩S:codegen-lowbat-{batt_type}.js',
                    'unit': 'mV',
                },
            ))

        # Zigbee channels
        channels.append(MQTT_ThingChannel(
            type='number',
            id='link',
            args={
                'stateTopic': state_topic,
                'transformationPattern': 'REGEX:(.*"linkquality".*)∩JSONPATH:$.linkquality',
            },
        ))
        channels.append(MQTT_ThingChannel(
            type='switch',
            id='ota',
            args={
                'stateTopic': state_topic,
                'transformationPattern': 'REGEX:(.*"update_available".*)∩JSONPATH:$.update_available',
                'on': 'true',
                'off': 'false',
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

    def get_things_petrows(self) -> List[Thing]:
        """
            Things for DIY devices.
            It has MQTT driven items, generate thing from this device
        """

        channels = []

        state_topic = f"petrows/{self.device_id}/STATE"

        # Device is DiY CO₂ sensor
        if self.has_tag('co2'):
            channels.append(MQTT_ThingChannel(
                type='number',
                id='co2',
                args={
                    'stateTopic': state_topic,
                    'transformationPattern': 'JSONPATH:$.S8.CO2',
                    'unit': 'ppm',
                },
            ))
            channels.append(MQTT_ThingChannel(
                type='switch',
                id='co2_led',
                args={
                    'stateTopic': state_topic,
                    'transformationPattern': 'JSONPATH:$.S8.led',
                    'on': '1',
                    'off': '0',
                },
            ))

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
            type='string',
            id='bssid',
            args={
                'stateTopic': state_topic,
                'transformationPattern': "JSONPATH:$.Wifi.BSSId",
            },
        ))
        # Monitoring?
        channels.append(MQTT_ThingChannel(
            type='datetime',
            id='activity',
            args={
                'stateTopic': state_topic,
                'transformationPattern': "JS:codegen-activity.js",
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

        # Monitoring?
        if self.has_monitoring():
            items.append(
                MQTT_Item(
                    id=f"{self.id}_activity",
                    name=f"{self.name} activity [JS(codegen-display-activity.js):%s]",
                    type='DateTime',
                    icon='time',
                    groups=self.get_groups(type='activity'),
                    broker=self.config['mqtt_broker_id'],
                    channel_id='activity',
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

        for metric in DEVICE_SIMPLE_CHANNELS:
            if self.has_tag(metric['id']):
                if 'icon' not in metric:
                    metric['icon'] = metric['id']
                items.append(
                    MQTT_Item(
                        id=f'{self.id}_{metric["id"]}',
                        name=f'{self.name} {metric["title"]}',
                        type=metric["type"],
                        icon=self.get_icon(default=metric["icon"]),
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
                        id=f"{channel_cfg['id']}",
                        name=channel_cfg['name'],
                        type='Switch',
                        icon=self.get_icon(default='light'),
                        groups=self.get_channel_groups(channel=channel['id'], type='sw'),
                        broker=self.config['mqtt_broker_id'],
                        channel_id=f'{self.id}:{channel["id"]}',
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
                    name=f'{self.name} CT [JS(codegen-mired.js): %s]',
                    type='Dimmer',
                    icon=self.get_icon(default='light'),
                    groups=self.get_groups(type='ct'),
                    broker=self.config['mqtt_broker_id'],
                    channel_id=f'{self.id}:ct',
                    sitemap_type='Slider',
                )
            )
            environment = jinja2.Environment(loader=jinja2.FileSystemLoader("rules/"))
            template = environment.get_template("ct_rule_header.rules")
            self.rules_header.extend(template.render(item=self).splitlines())
            template = environment.get_template("ct_rule.rules")
            self.rules.extend(template.render(item=self).splitlines())

        # Some zigbee lamps have color
        if self.has_tag('color'):
            items.append(
                MQTT_Item(
                    id=f"{self.id}_color",
                    name=f'{self.name} Color',
                    type='Color',
                    icon='colorwheel',
                    groups=self.get_groups(type='color'),
                    broker=self.config['mqtt_broker_id'],
                    channel_id=f'{self.id}:color',
                    sitemap_type='Colorpicker',
                )
            )
            items.append(
                MQTT_Item(
                    id=f"{self.id}_color_mode",
                    name=f'{self.name} Color mode',
                    type='String',
                    icon='colorwheel',
                    groups=self.get_groups(type='color_mode'),
                    broker=self.config['mqtt_broker_id'],
                    channel_id=f'{self.id}:color_mode',
                    sitemap_type='Text',
                )
            )

        if self.has_tag('remote'):
            # Simulate brightness?
            if self.is_simulated_brightness():
                items.append(
                    MQTT_Item(
                        id=f"{self.id}_dim",
                        name=f'{self.name} DIM [%d %%]',
                        type='Dimmer',
                        icon=self.get_icon(default='light'),
                        groups=self.get_groups(type='dim'),
                        broker=self.config['mqtt_broker_id'],
                        channel_id=f'{self.id}:dim',
                        sitemap_type='Text',
                    )
                )

        if self.has_tag('thermostat'):
            items.append(
                MQTT_Item(
                    id=f"{self.id}_thermostat",
                    name=f'{self.name} SET [%.0f %unit%]',
                    type='Number:Temperature',
                    icon='heatingt',
                    groups=self.get_groups(type='thermostat'),
                    broker=self.config['mqtt_broker_id'],
                    channel_id=f'{self.id}:thermostat',
                    sitemap_type='Setpoint',
                )
            )
            items.append(
                MQTT_Item(
                    id=f"{self.id}_thermostat_mode",
                    name=f'{self.name} MODE [%s]',
                    type='String',
                    icon='heatingt',
                    groups=self.get_groups(type='thermostat_mode'),
                    broker=self.config['mqtt_broker_id'],
                    channel_id=f'{self.id}:thermostat_mode',
                    sitemap_type='Text',
                )
            )
            items.append(
                MQTT_Item(
                    id=f"{self.id}_thermostat_enable",
                    name=f'{self.name} ENABLE [%s]',
                    type='Switch',
                    icon='heatingt',
                    groups=self.get_groups(type='thermostat_enable'),
                    broker=self.config['mqtt_broker_id'],
                    channel_id=f'{self.id}:thermostat_enable',
                    sitemap_type='Switch',
                )
            )

        # Battery control
        if self.has_tag_any('battery', 'battery_low', 'battery_voltage'):
            items.append(
                MQTT_Item(
                    id=f"{self.id}_lowbatt",
                    name=f'{self.name} BAT [MAP(codegen-lowbat.map):%s]',
                    type='Switch',
                    icon='lowbattery',
                    groups=self.get_groups(type='lowbattery'),
                    broker=self.config['mqtt_broker_id'],
                    channel_id=f'{self.id}:battery_low',
                    sitemap_type='Text',
                )
            )

        # Common Zigbee channels
        items.append(
            MQTT_Item(
                id=f"{self.id}_ota",
                name=f'{self.name} OTA [%s]',
                type='Switch',
                icon='fire',
                groups=self.get_groups(type='ota'),
                broker=self.config['mqtt_broker_id'],
                channel_id=f'{self.id}:ota',
                sitemap_type='Text',
            )
        )
        items.append(
            MQTT_Item(
                id=f"{self.id}_link",
                name=f'{self.name} LINK [%d]',
                type='Number:Dimensionless',
                icon='linkz',
                groups=self.get_groups(type='link'),
                broker=self.config['mqtt_broker_id'],
                channel_id=f'{self.id}:link',
                sitemap_type='Text',
            )
        )


        return items
