"""Voltalis current power sensor."""

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfPower

from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity


class VoltalisCurrentPowerSensor(VoltalisEntity, SensorEntity):
    """Representation of a Voltalis current power sensor."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_icon = "mdi:flash"
    _attr_translation_key = "current_power"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        data = self.coordinator.data.get(self.device_id)
        if data is None:
            return None
        return data.current_power
