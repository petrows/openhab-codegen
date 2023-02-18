// Thermostat does not have built-in on/off modes,
// use 5°C setting as on/off toggle

(function(x) {
    if (x == '1' || x == 'ON') {
        return '' // Do nothing
    }
    cmd = { current_heating_setpoint: '5' }
    return JSON.stringify(cmd)
})(input)
