from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity

from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity


class VoltalisManualModeSensor(VoltalisEntity, BinarySensorEntity):
    """Binary sensor for manual mode status."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_translation_key = "manual_mode"
    _attr_entity_registry_enabled_default = False
    _unique_id_suffix = "manual_mode"

    @property
    def is_on(self) -> bool | None:
        """Return true if manual mode is enabled."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.manual_setting:
            return data.manual_setting.enabled
        return None
