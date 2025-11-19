from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)


class VoltalisProgrammingNameSensor(VoltalisEntity, SensorEntity):
    """Sensor for programming name."""

    _attr_translation_key = "programming_name"
    _attr_entity_registry_enabled_default = False
    _unique_id_suffix = "programming_name"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        data = self.coordinator.data.get(self._device.id)
        if data is None:
            _LOGGER.warning("Device %s not found in coordinator data", self._device.id)
            return

        new_value = data.device.programming.prog_name
        if new_value is None or self.native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: object) -> bool:  # type: ignore[override]
        if data is None:
            return False
        # Safe attribute access with getattr (coordinator data model has .device.programming.prog_name)
        device = getattr(data, "device", {})
        programming = getattr(device, "programming", {})
        return getattr(programming, "prog_name", None) is not None
