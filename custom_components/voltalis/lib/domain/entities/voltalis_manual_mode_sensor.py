from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)


class VoltalisManualModeSensor(VoltalisEntity, BinarySensorEntity):
    """Binary sensor for manual mode status."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_translation_key = "manual_mode"
    _attr_entity_registry_enabled_default = False
    _unique_id_suffix = "manual_mode"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        data = self.coordinator.data.get(self._device.id)
        if data is None:
            _LOGGER.warning("Device %s not found in coordinator data", self._device.id)
            return

        if data.manual_setting is None:
            _LOGGER.warning("Device %s has no manual_setting in coordinator data", self._device.id)
            return

        new_value = data.manual_setting.enabled
        if new_value is None or self.is_on == new_value:
            return

        self._attr_is_on = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: object) -> bool:  # type: ignore[override]
        if data is None:
            return False
        # Safe attribute access with getattr (coordinator data model has .manual_setting.enabled)
        manual_setting = getattr(data, "manual_setting", {})
        return getattr(manual_setting, "enabled", None) is not None
