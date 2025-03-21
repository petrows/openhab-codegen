#!/usr/bin/env python3

# # Devices, used in this configuration
from ast import Str
from typing import Any

from codegen.device import Device

class DEVICES:
    """
        This staitc class: supported device registry

        types: array of 'tags' for this device:

            * tasmota : device is Tamota driven (mqtt)
            * zigbee : device is Zigbee network (zigbee2mqtt)

            * lamp : device is lamp (has ON/OFF channel)
            * activity : device is checked for activity
            * rssi : device reports WiFi network name
            * bssid : device reports WiFi basic station MAC
            * la : device reports Load Average
    """

    def get_from_id(self, id: Str) -> Any:
        return getattr(self, id)

    def get_device(self, device_config, global_config) -> Device:
        # Find device config from DEVICES object
        type_config = self.get_from_id(id=device_config['type'])
        # Create device class
        device = Device(device_config, type_config)
        device.set_global_config(global_config)
        return device

    # =========================================================================

    # IKEA Lamps
    IKEA_TRADFRI_LAMP_CLEAR_806 = {
        'types': [
            'zigbee',
            'lamp',
            'ikea',
            'ct',
        ],
        'device_name': 'IKEA TRADFRI LED bulb E27 806 lumen, dimmable, white spectrum, clear (LED1736G9)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/LED1736G9.html',
        # 'ct_max': 454,
    }
    IKEA_TRADFRI_LAMP_CT_1000 = {
        'types': [
            'zigbee',
            'lamp',
            'ikea',
            'ct',
        ],
        'device_name': 'IKEA TRADFRI LED bulb E27 1000 lumen, dimmable, white spectrum, opal white (LED1732G11)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/LED1732G11.html',
        # 'ct_min': 250,
        # 'ct_max': 454,
    }
    IKEA_TRADFRI_LAMP_LED2003G10 = {
        'types': [
            'zigbee',
            'lamp',
            'ikea',
            'ct',
        ],
        'device_name': 'IKEA TRADFRI LED bulb E26/27 1100/1055/1160 lumen, dimmable, white spectrum, opal white (LED2003G10)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/LED2003G10.html',
        'dim_min': 2,  # Device turns OFF on brightness = 1, enlarge limit to 2
        # 'ct_min': 250,
        # 'ct_max': 454,
    }
    IKEA_TRADFRI_LAMP_LED1546G12 = {
        'types': [
            'zigbee',
            'lamp',
            'ikea',
            'ct',
            'ct_startup',
        ],
        'device_name': 'TRADFRI LED bulb E26/E27 950 lumen, dimmable, white spectrum, clear (LED1546G12)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/LED1546G12.html',
        'dim_min': 2, # Device turns OFF on brightness = 1, enlarge limit to 2
        # 'ct_min': 250,
        # 'ct_max': 454,
    }
    IKEA_TRADFRI_LAMP_LED2101G4 = {
        'types': [
            'zigbee',
            'lamp',
            'ikea',
            'ct',
            'ct_startup',
        ],
        'device_name': 'TRADFRI bulb E12/E14 WS globe 450/470 lumen, dimmable, white spectrum, opal white',
        'device_url': 'https://www.zigbee2mqtt.io/devices/LED2101G4.html',
    }
    IKEA_TRADFRI_LAMP_W_806 = {
        'types': [
            'zigbee',
            'lamp',
            'ikea',
        ],
        'device_name': 'IKEA TRADFRI LED bulb E26/E27 806 lumen, dimmable, warm white (LED1836G9)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/LED1836G9.html',
    }
    IKEA_TRADFRI_LAMP_W_250 = {
        'types': [
            'zigbee',
            'lamp',
            'ikea',
        ],
        'device_name': 'IKEA TRADFRI LED bulb E27 WW clear 250 lumen, dimmable (LED1842G3)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/LED1842G3.html',
    }
    IKEA_TRADFRI_LED_DRIVER = {
        'types': [
            'zigbee',
            'lamp',
            'ikea',
        ],
        'device_name': 'IKEA TRADFRI driver for wireless control',
        'device_url': 'https://www.zigbee2mqtt.io/devices/ICPSHC24-10EU-IL-1.html',
    }
    IKEA_TRADFRI_LAMP_COLOR_600 = {
        'types': [
            'zigbee',
            'lamp',
            'ikea',
            'color',
            'ct',
        ],
        'device_name': 'TRADFRI LED bulb E14/E26/E27 600 lumen, dimmable, color, opal white (ebay)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/LED1624G9.html',
        # 'ct_max': 454,
    }
    # IKEA Motion
    IKEA_TRADFRI_MOTION_SENSOR = {
        'types': [
            'zigbee',
            'occupancy',
            'ikea',
            'activity',
            'battery',
        ],
        'device_name': 'IKEA TRADFRI motion sensor (E1525/E1745)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/E1525_E1745.html',
    }
    # IKEA Remotes
    # The possible values are: toggle, arrow_left_click, arrow_right_click, arrow_left_hold, arrow_right_hold, arrow_left_release, arrow_right_release, brightness_up_click, brightness_down_click, brightness_up_hold, brightness_up_release, brightness_down_release, toggle_hold
    IKEA_TRADFRI_REMOTE = {
        'types': [
            'zigbee',
            'remote',
            'ikea',
            'battery',
        ],
        'device_name': 'IKEA TRADFRI remote control (E1524/E1810)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/E1524_E1810.html',
    }
    # The possible values are: on, off, brightness_move_down, brightness_move_up, brightness_stop
    IKEA_TRADFRI_ON_OFF = {
        'types': [
            'zigbee',
            'remote',
            'ikea',
            'battery',
        ],
        'device_name': 'IKEA TRADFRI ON/OFF switch (E1743)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/E1743.html',
    }
    # The possible values are: on, off, brightness_move_down, brightness_move_up, brightness_stop
    IKEA_TRADFRI_CURTAIN_REMOTE = {
        'types': [
            'zigbee',
            'remote',
            'ikea',
            'battery',
        ],
        'device_name': 'IKEA TRADFRI open/close remote (E1766)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/E1766.html',
    }
    # The possible values are: on, off, brightness_move_up, brightness_move_down, brightness_stop, arrow_left_click, arrow_right_click, arrow_left_hold, arrow_right_hold, arrow_left_release, arrow_right_release
    IKEA_TRADFRI_STYRBAR = {
        'types': [
            'zigbee',
            'remote',
            'simulated_brightness',
            'ikea',
            'battery',
        ],
        'simulated_brightness': True,
        'device_name': 'IKEA STYRBAR remote control N2',
        'device_url': 'https://www.zigbee2mqtt.io/devices/E2001_E2002.html',
    }
    IKEA_PARASOLL = {
        'types': [
            'zigbee',
            'contact',
            'ikea',
            # Seems to be buggy, see https://github.com/Koenkk/zigbee2mqtt/issues/22579
            'activity',
            'battery',
        ],
        'device_name': 'PARASOLL Door/Window Sensor (E2013)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/E2013.html',
    }
    IKEA_BADRING = {
        'types': [
            'zigbee',
            'leak',
            'ikea',
            'activity',
            'battery',
        ],
        'mqtt_remap': { 'leak': 'water_leak' },
        'device_name': 'BADRING water leakage sensor (E2202)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/E2202.html',
    }
    IKEA_VALLHORN = {
        'types': [
            'zigbee',
            'occupancy',
            'ikea',
            'illuminance_lux',
            'illuminance',
            'activity',
            'battery',
        ],
        'device_name': 'VALLHORN wireless motion sensor (E2134)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/E2134.html',
    }
    IKEA_TRETAKT = {
        'types': [
            'zigbee',
            'plug',
            'ikea',
        ],
        'device_name': 'TRETAKT smart plug (E22x4)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/E22x4.html',
    }
    IKEA_INSPELNING = {
        'types': [
            'zigbee',
            'plug',
            'ikea',
            'ac_current',
            'ac_energy',
            'ac_power',
            'ac_voltage',
        ],
        'device_name': 'INSPELNING smart plug (E2206)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/E2206.html',
    }
    # Sockets
    OSRAM_SMART_PLUG = {
        'types': [
            'zigbee',
            'plug',
        ],
        'device_name': 'OSRAM Smart+ plug',
        'device_url': 'https://www.zigbee2mqtt.io/devices/AB3257001NJ.html',
    }
    # Xiaomi sensors
    XIAOMI_AQARA_V1 = {
        'types': [
            'zigbee',
            'temperature',
            'humidity',
            'activity',
            'battery',
            'voltage',
        ],
        'device_name': 'Xiaomi MiJia temperature & humidity sensor (WSDCGQ01LM)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/WSDCGQ01LM.html',
    }
    XIAOMI_AQARA_V2 = {
        'types': [
            'zigbee',
            'temperature',
            'humidity',
            'pressure',
            'activity',
            'battery',
            'voltage',
        ],
        'device_name': 'Xiaomi Aqara temperature, humidity and pressure sensor (WSDCGQ11LM)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/WSDCGQ11LM.html',
    }
    XIAOMI_AQARA_LEAK_V1 = {
        'types': [
            'zigbee',
            'leak',
            'activity',
            'battery',
            'voltage',
        ],
        'device_name': 'Xiaomi Aqara water leak sensor (SJCGQ11LM)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/SJCGQ11LM.html',
    }
    # The possible values are: single, double, tripple, quadruple, hold, release
    XIAOMI_BUTTON = {
        'types': [
            'zigbee',
            'remote',
            'battery',
            'voltage',
        ],
        'device_name': 'Xiaomi MiJia wireless switch (WXKG01LM)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/WXKG01LM.html',
    }
    # Aldi
    ALDI_FILAMENT = {
        'types': [
            'zigbee',
            'lamp',
            'aldi',
            'ct',
        ],
        'device_name': 'Aldi LIGHTWAY smart home LED-lamp - filament (F122SB62H22A4.5W)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/F122SB62H22A4.5W.html',
    }
    # Heiman
    HEIMAN_SW_1_GANG = {
        'types': [
            'zigbee',
            'plug',
            'heiman',
            'device_temperature',
        ],
        'device_name': 'HEIMAN Smart switch - 1 gang with neutral wire (HS2SW1A/HS2SW1A-N)',
        'device_url': 'https://zigbee.blakadder.com/Heiman_HS2SW1A.html',
    }
    # Tuya
    TUYA_THERMOSTAT_VALVE = {
        'types': [
            'zigbee',
            'thermostat',
            'temperature',
            'local_temperature',
            'position',
            'activity',
            # 'battery_low', # For using akkus - invalid battery level reporting
        ],
        'thermostat_control_mode': "preset",  # Has "preset" option
        'device_name': 'TuYa Radiator valve with thermostat (TS0601_thermostat)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/TS0601_thermostat.html',
    }
    TUYA_THERMOSTAT_VALVE_3 = {
        'types': [
            'zigbee',
            'thermostat',
            'local_temperature',
            'activity',
            'battery_low',
        ],
        'thermostat_control_mode': "system_mode",
        'device_name': 'TuYa Radiator valve with thermostat (TS0601_thermostat 3)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/TS0601_thermostat_3.html',
    }
    TUYA_WINDOW_SENSOR = {
        'types': [
            'zigbee',
            'contact',
            'activity',
            'battery',
            'voltage',
        ],
        'device_name': 'TuYa Rechargeable Zigbee contact sensor (SNTZ007)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/SNTZ007.html',
    }
    TUYA_WINDOW_SENSOR_TS0203 = {
        'types': [
            'zigbee',
            'contact',
            'activity',
            'battery',
            'voltage',
        ],
        'device_name': 'TuYa Rechargeable Zigbee contact sensor (TS0203)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/TS0203.html#tuya-ts0203',
    }
    TUYA_TEMPERATURE_SENSOR_TS0201 = {
        'types': [
            'zigbee',
            'temperature',
            'humidity',
            'activity',
            'battery',
            'voltage',
        ],
        'device_name': 'TuYa Temperature & humidity sensor',
        'device_url': 'https://www.zigbee2mqtt.io/devices/TS0201.html',
    }
    TUYA_WALL_RELAY = {
        'types': [
            'zigbee',
            'contact',
            'battery',
            'voltage',
        ],
        'device_name': 'TuYa Wall switch module (WHD02)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/WHD02.html',
    }
    TUYA_WALL_DIMMER = {
        'types': [
            'zigbee',
            'lamp',
        ],
        'dim_min': 30,
        'transition_sw': 0,
        'transition_brightness': 0,
        # 'proxy_state': True,  # Filter repeating state commands
        # Reuqst device status after filtering?
        # This device triggers state after request
        # 'proxy_state_request': False,
        'device_name': 'TuYa Wall dimmer module (TS110E_1gang_1)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/TS110E_1gang_1.html#tuya-ts110e_1gang_1',
    }
    TUYA_WALL_SWITCH_TS0601 = {
        'types': [
            'zigbee',
            'plug_mt',
        ],
        'device_name': 'TS0601_switch - TuYa 1, 2, 3 or 4 gang switch (Router)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/TS0601_switch.html',
    }
    TUYA_SWITCH_TS0001 = {
        'types': [
            'zigbee',
            'plug',
        ],
        'device_name': 'Wall switch module',
        'device_url': 'https://www.zigbee2mqtt.io/devices/WHD02.html#tuya-whd02',
    }
    # Tyua Zigbee socket with power meter
    TUYA_PLUG_TS000F = {
        'types': [
            'zigbee',
            'plug',
            'ac_current',
            'ac_energy',
            'ac_power',
            'ac_voltage',
        ],
        'device_name': 'Plug socket with power function',
        'device_url': 'https://www.zigbee2mqtt.io/devices/TS000F_power.html',
    }


    # Lidl smart home - Silvercrest
    SILVERCREST_SMART_PLUG = {
        'types': [
            'zigbee',
            'plug',
        ],
        'device_name': 'Lidl Silvercrest smart plug (EU, CH, FR, BS, DK) (HG06337)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/HG06337.html',
    }
    SILVERCREST_SMART_BUTTON = {
        'types': [
            'zigbee',
            'remote',
            'battery',
            'voltage',
        ],
        'device_name': 'Lidl Silvercrest smart button (HG08164)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/HG08164.html',
    }
    LIVARNO_CELLING = {
        'types': [
            'zigbee',
            'lamp',
            'ct',
            'color',
        ],
        # Workaround: https://github.com/Koenkk/zigbee2mqtt/issues/14714
        'proxy_state': True,  # Filter repeating state commands
        'device_name': 'Livarno Home LED ceiling light (HG08008)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/HG08008.html#lidl-hg08008',
    }
    LIVARNO_CELLING_14147206L = {
        'types': [
            'zigbee',
            'lamp',
            'ct',
        ],
        'device_name': 'Livarno Home Lux ceiling light (14147206L)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/14147206L.html#lidl-14147206l',
    }
    LIVARNO_RGB_HG07834B = {
        'types': [
            'zigbee',
            'lamp',
            'ct',
            'color',
        ],
        # Workaround: https://github.com/Koenkk/zigbee2mqtt/issues/14714
        'proxy_state': True,  # Filter repeating state commands
        'device_name': 'Livarno Lux E14 candle RGB (HG07834B)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/HG07834B.html#lidl-hg07834b',
    }

    # Zemnismart 3-phase power meter
    ZEMNISMART_3PHASE_METER = {
        'types': [
            'zigbee',
            'zigbee',
            'ac_power_factor',
            'ac_frequency',
            'ac_energy',
            'ac_power',
            'ac_voltage_a',
            'ac_voltage_b',
            'ac_voltage_c',
            'ac_current_a',
            'ac_current_b',
            'ac_current_c',
            'ac_power_a',
            'ac_power_b',
            'ac_power_c',
        ],
        'device_name': 'Smart energy monitor for 3P+N system',
        'device_url': 'https://www.zigbee2mqtt.io/devices/SPM02V2.5.html#tuya-spm02v2.5',
    }


    # DIY
    DIY_CC2540_ROUTER = {
        'types': [
            'zigbee',
        ],
        'device_name': 'CC2530.ROUTER - Custom devices (DiY)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/CC2530.ROUTER.html',
    }
    # Sonoff-tasmota
    TASMOTA_SONOFF_MINI = {
        'types': [
            'tasmota',
            'activity',
            'rssi',
            'bssid',
            'la',
        ],
        'device_name': 'Sonoff Mini Switch',
        'device_url': 'https://templates.blakadder.com/sonoff_mini.html',
        'tasmota_channels': [
            {
                'type': 'switch',
                'id': 'POWER',
            }
        ]
    }
    TASMOTA_SONOFF_TOUCH_EU1 = {
        'types': [
            'tasmota',
            'activity',
            'rssi',
            'bssid',
            'la',
        ],
        'device_name': 'Sonoff Touch EU Switch (1 gang)',
        'device_url': 'https://templates.blakadder.com/sonoff_touch_eu.html',
        'tasmota_channels': [
            {
                'type': 'switch',
                'id': 'POWER',
            }
        ]
    }
    TASMOTA_SONOFF_TOUCH_EU2 = {
        'types': [
            'tasmota',
            'activity',
            'rssi',
            'bssid',
            'la',
        ],
        'device_name': 'Sonoff Touch EU Switch (2 gang)',
        'device_url': 'https://templates.blakadder.com/sonoff_touch_eu.html',
        'tasmota_channels': [
            {
                'type': 'switch',
                'id': 'POWER1',
            },
            {
                'type': 'switch',
                'id': 'POWER2',
            }
        ]
    }
    TASMOTA_RGBW = {
        'types': [
            'tasmota',
            'activity',
            'rssi',
            'bssid',
            'la',
            'ct',
            'color',
        ],
        'device_name': 'Tasmota RGB+W dimmer',
        'device_url': 'https://templates.blakadder.com/arilux_LC06.html',
        'tasmota_channels': [
            {
                'type': 'switch',
                'id': 'POWER',
            },
            {
                'type': 'dimmer',
                'id': 'Dimmer',
                'mode': 'dimmer',
            },
            {
                'type': 'dimmer',
                'id': 'White',
                'mode': 'dimmer',
            },
            {
                'type': 'dimmer',
                'id': 'CT',
                'mode': 'ct',
            },
            {
                'type': 'color',
                'id': 'HSBColor',
                'mode': 'color',
            },
        ]
    }
    # Wemos D1 + Senseair S8
    # tele/sz_co2/SENSOR {"Time":"2023-01-27T17:41:07","S8":{"CarbonDioxide":1352}}
    TASMOTA_WEMOS_CO2 = {
        'types': [
            'tasmota',
            'activity',
            'rssi',
            'bssid',
            'la',
        ],
        'device_name': 'ESP8266 + Senseair S8',
        'device_url': '',
        'tasmota_channels': [
            {
                'type': 'co2',
                'id': 'S8',
            },
        ]
    }
    # PWS room sensor v2
    # SENSOR = {"Time":"2024-11-21T22:42:47","BMP280":{"Temperature":21.4,"Pressure":983.2},"S8":{"CarbonDioxide":620},"AHT2X":{"Temperature":20.4,"Humidity":49.0,"DewPoint":9.3},"PressureUnit":"hPa","TempUnit":"C"}
    TASMOTA_PWS_ROOM_SENSOR_V2 = {
        'types': [
            'tasmota',
            'activity',
            'rssi',
            'bssid',
            'la',
            'co2',
            'temperature',
            'humidity',
            'dewpoint',
            'pressure',
        ],
        'device_name': 'PWS room sensor v2',
        'device_url': 'https://oshwlab.com/petrows/wemos-d1-room-sensor',
        'tasmota_channels': [
            # R
            {
                'type': 'switch',
                'id': 'POWER1',
            },
            # Y
            {
                'type': 'switch',
                'id': 'POWER2',
            },
            # G
            {
                'type': 'switch',
                'id': 'POWER3',
            },
        ],
        'tasmota_sensors': [
            {
                'id': 'co2',
                'type': 'co2',
                'path': '.S8.CarbonDioxide',
            },
            {
                'id': 'temperature',
                'type': 'temperature',
                'path': '.AHT2X.Temperature',
            },
            {
                'id': 'humidity',
                'type': 'humidity',
                'path': '.AHT2X.Humidity',
            },
            {
                'id': 'dewpoint',
                'type': 'temperature',
                'path': '.AHT2X.DewPoint',
            },
            {
                'id': 'pressure',
                'type': 'pressure',
                'path': '.BMP280.Pressure',
            },
        ]
    }
    # Reduced version (no co2)
    TASMOTA_PWS_ROOM_SENSOR_V2_NOCO2 = {
        'types': [
            'tasmota',
            'activity',
            'rssi',
            'bssid',
            'la',
            'temperature',
            'humidity',
            'dewpoint',
            'pressure',
        ],
        'device_name': 'PWS room sensor v2 (no co2)',
        'device_url': 'https://oshwlab.com/petrows/wemos-d1-room-sensor',
        'tasmota_channels': [],
        'tasmota_sensors': [
            {
                'id': 'temperature',
                'type': 'temperature',
                'path': '.AHT2X.Temperature',
            },
            {
                'id': 'humidity',
                'type': 'humidity',
                'path': '.AHT2X.Humidity',
            },
            {
                'id': 'dewpoint',
                'type': 'temperature',
                'path': '.AHT2X.DewPoint',
            },
            {
                'id': 'pressure',
                'type': 'pressure',
                'path': '.BMP280.Pressure',
            },
        ]
    }

    SILVERCREST_THERMOSTAT_368308_2010 = {
        'types': [
            'zigbee',
            'thermostat',
            'local_temperature',
            'activity',
            'voltage',
            'battery_voltage',
        ],
        # Device reports value seems to be 'per element' (it has 2xAA)
        'batt_type': '1xAA',
        'thermostat_control_mode': "system_mode",
        'device_name': 'Silvercrest radiator valve with thermostat',
        'device_url': 'https://www.zigbee2mqtt.io/devices/368308_2010.html',
    }
    SITERWELL_THERMOSTAT_GS361A = {
        'types': [
            'zigbee',
            'thermostat',
            'local_temperature',
            'activity',
            'battery',
        ],
        # Device reports value seems to be 'per element' (it has 2xAA)
        'batt_type': '1xAA',
        'thermostat_control_mode': "system_mode",
        'device_name': 'Siterwell GS361A-H04 valve with thermostat',
        'device_url': 'https://www.zigbee2mqtt.io/devices/GS361A-H04.html',
    }

    # MOES devices

    MOES_THERMOSTAT_BRT_100 = {
        'types': [
            'zigbee',
            'thermostat',
            'local_temperature',
            'position',
            'activity',
            'battery',
        ],
        'thermostat_control_mode': "5c",
        'device_name': 'Moes BRT-100-TRV thermostat',
        'device_url': 'https://www.zigbee2mqtt.io/devices/BRT-100-TRV.html',
    }
    MOES_SWITCH_ZS_EUB_1GANG = {
        'types': [
            'zigbee',
            'plug',
        ],
        'device_name': 'Wall light switch (1 gang)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/ZS-EUB_1gang.html',
    }

    # Lonsonho universal devices
    BLINDS_MODULE_TS130F_1CH = {
        'types': [
            'zigbee',
            'blinds',
        ],
        'device_name': 'Curtains module (1 gang)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/TS130F.html',
    }
    BLINDS_MODULE_TS130F_2CH = {
        'types': [
            'zigbee',
            'blinds_mt',
        ],
        'device_name': 'Curtains module (2 gang)',
        'device_url': 'https://www.zigbee2mqtt.io/devices/TS130F_dual.html',
    }

    # DIY devices by author

    PETROWS_CO2_SENSOR = {
        'types': [
            'petrows',
            'activity',
            'co2',
            'co2_led',
            'dht22',
            'temperature',
            'humidity',
            'rssi',
            'bssid',
        ],
        'device_name': 'Petro.ws CO₂ sensor module',
        'device_url': 'https://github.com/petrows/smarthome-co2-module',
    }
