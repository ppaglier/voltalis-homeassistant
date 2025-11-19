from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity

from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity


class VoltalisProgrammingTypeSensor(VoltalisEntity, SensorEntity):
    """Sensor for programming type (MANUAL, DEFAULT, USER)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "programming_type"
    _attr_options = ["MANUAL", "DEFAULT", "USER"]
    _attr_entity_registry_enabled_default = False
    _unique_id_suffix = "programming_type"

    @property
    def native_value(self) -> str | None:
        """Return the programming type."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.device and data.device.programming:
            return str(data.device.programming.prog_type)
        return None
