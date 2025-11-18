from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass

from custom_components.voltalis.lib.domain.device import VoltalisDevice
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity
from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator


class VoltalisManualModeSensor(VoltalisEntity, BinarySensorEntity):
    """Binary sensor for manual mode status."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_translation_key = "manual_mode"

    def __init__(self, coordinator: VoltalisCoordinator, device: VoltalisDevice) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_manual_mode"
        self._attr_name = "Manual mode"

    @property
    def is_on(self) -> bool | None:
        """Return true if manual mode is enabled."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.manual_setting:
            return data.manual_setting.enabled
        return None
