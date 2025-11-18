from __future__ import annotations

from homeassistant.components.sensor import SensorEntity

from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator
from custom_components.voltalis.lib.domain.device import VoltalisDevice
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity


class VoltalisProgrammingNameSensor(VoltalisEntity, SensorEntity):
    """Sensor for programming name."""

    _attr_translation_key = "programming_name"

    def __init__(self, coordinator: VoltalisCoordinator, device: VoltalisDevice) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_programming_name"
        self._attr_name = "Programming name"

    @property
    def native_value(self) -> str | None:
        """Return the programming name."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.device and data.device.programming:
            return data.device.programming.prog_name
        return None
