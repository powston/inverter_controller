from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)

class InverterSensor(SensorEntity):
    """Representation of an Inverter with PV and Battery."""

    __attr_names = [
        "pv_power",
        "pv_voltage",
        "pv_current",
        "battery_power",
        "battery_voltage",
        "battery_current",
        "battery_soc",
        "load_power",
        "load_voltage",
        "load_current",
        "grid_power",
        "grid_voltage",
        "grid_current",
        "frequency",
        "power_factor",
        "temperature",
        "energy_today",
        "energy_total",
    ]
    _attr_native_values = {name: None for name in __attr_names}
    _attr_device_classes = {
        "pv_power": SensorDeviceClass.POWER,
        "pv_voltage": SensorDeviceClass.VOLTAGE,
        "pv_current": SensorDeviceClass.CURRENT,
        "battery_power": SensorDeviceClass.POWER,
        "battery_voltage": SensorDeviceClass.VOLTAGE,
        "battery_current": SensorDeviceClass.CURRENT,
        "battery_soc": SensorDeviceClass.PERCENTAGE,
        "load_power": SensorDeviceClass.POWER,
        "load_voltage": SensorDeviceClass.VOLTAGE,
        "load_current": SensorDeviceClass.CURRENT,
        "grid_power": SensorDeviceClass.POWER,
        "grid_voltage": SensorDeviceClass.VOLTAGE,
        "grid_current": SensorDeviceClass.CURRENT,
        "frequency": SensorDeviceClass.FREQUENCY,
        "power_factor": SensorDeviceClass.POWER_FACTOR,
        "temperature": SensorDeviceClass.TEMPERATURE
    }
    
    def __init__(self, site_name, inverter_id, model_name, serial_number):
        """Initialize the sensor."""
        self.site_name = site_name
        self.inverter_id = inverter_id
        self.model_name = model_name
        self.serial_number = serial_number
        self.last_interval = None

    @property
    def unique_id(self):
        return f"powston_inverter_{self.inverter_id}"


    @property
    def state_attributes(self):
        """Return the state attributes of the sensor."""
        attributes = super().state_attributes or {}
        for name in self.__attr_names:
            value = self._attr_native_values[name]
            if value is not None:
                attributes[name] = value
        return attributes
    
    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{self.site_name} {self.model_name} {self.serial_number}"
    

    def set_value(self, name, value):
        """Set a value."""
        if name in self.__attr_names:
            self._attr_native_values[name] = value
            self.async_write_ha_state()
