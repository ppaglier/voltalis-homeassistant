from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass

from custom_components.voltalis.lib.domain.device import VoltalisDevice
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity
from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator


class VoltalisProgrammingTypeSensor(VoltalisEntity, SensorEntity):
    """Sensor for programming type (MANUAL, DEFAULT, USER)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "programming_type"

    def __init__(self, coordinator: VoltalisCoordinator, device: VoltalisDevice) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_programming_type"
        self._attr_name = "Programming type"
        self._attr_options = ["MANUAL", "DEFAULT", "USER"]

    @property
    def native_value(self) -> str | None:
        """Return the programming type."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.device and data.device.programming:
            return str(data.device.programming.prog_type)
        return None
