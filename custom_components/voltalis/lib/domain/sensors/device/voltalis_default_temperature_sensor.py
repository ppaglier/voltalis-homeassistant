from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfTemperature

from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator
from custom_components.voltalis.lib.domain.device import VoltalisDevice
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity


class VoltalisDefaultTemperatureSensor(VoltalisEntity, SensorEntity):
    """Sensor for default temperature setting."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_translation_key = "default_temperature"

    def __init__(self, coordinator: VoltalisCoordinator, device: VoltalisDevice) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_default_temperature"
        self._attr_name = "Default temperature"

    @property
    def native_value(self) -> float | None:
        """Return the default temperature."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.device and data.device.programming:
            return data.device.programming.default_temperature
        return None
