from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE

from custom_components.voltalis.lib.domain.device import VoltalisDevice
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity
from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator


class VoltalisHeatingLevelSensor(VoltalisEntity, SensorEntity):
    """Sensor for heating level percentage."""

    _attr_device_class = SensorDeviceClass.POWER_FACTOR
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_translation_key = "heating_level"

    def __init__(self, coordinator: VoltalisCoordinator, device: VoltalisDevice) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_heating_level"
        self._attr_name = "Heating level"

    @property
    def native_value(self) -> int | None:
        """Return the heating level."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.device:
            return data.device.heating_level
        return None
