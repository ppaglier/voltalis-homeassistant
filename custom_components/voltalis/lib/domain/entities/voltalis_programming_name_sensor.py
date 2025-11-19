from __future__ import annotations

from homeassistant.components.sensor import SensorEntity

from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity


class VoltalisProgrammingNameSensor(VoltalisEntity, SensorEntity):
    """Sensor for programming name."""

    _attr_translation_key = "programming_name"
    _attr_entity_registry_enabled_default = False
    _unique_id_suffix = "programming_name"

    @property
    def native_value(self) -> str | None:
        """Return the programming name."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.device and data.device.programming:
            return data.device.programming.prog_name
        return None
