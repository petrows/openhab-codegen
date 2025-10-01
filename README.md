# Openhab code genrator

Generates repeated configs for Zigbbe / Tasmota devices,
based on MQTT binding.

Uses multiply configs.

## Device options

### Thermostats

`thermostat_control_mode` - How to control thermostat ON/OFF options.
Possible options:

* `system_mode` - (default) means that thermostat has `system_mode` channel,
which accepts `off` (thermostat disabled) and `heat` (thermostat enabled) options.
* `preset` - means that thermostat controlled via `preset` channel, which accepts
commands `holiday` (thermostat disabled) and `manual` (thermostat enabled).
* `5c` - device does not have built-in on/off control, just use 5°C threshold.
