from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.models.device import VoltalisDeviceProgTypeEnum
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)


class VoltalisProgrammingTypeSensor(VoltalisEntity, SensorEntity):
    """Sensor for programming type (MANUAL, DEFAULT, USER)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "programming_type"
    _attr_options = [option for option in VoltalisDeviceProgTypeEnum]
    _attr_entity_registry_enabled_default = False
    _unique_id_suffix = "programming_type"

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        if self.native_value is None:
            return "mdi:calendar-minus"
        if self.native_value == VoltalisDeviceProgTypeEnum.USER:
            return "mdi:calendar-account-outline"
        if self.native_value == VoltalisDeviceProgTypeEnum.MANUAL:
            return "mdi:calendar-edit-outline"
        if self.native_value == VoltalisDeviceProgTypeEnum.QUICK:
            return "mdi:calendar-clock-outline"
        return "mdi:calendar-blank-outline"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        data = self.coordinator.data.get(self._device.id)
        if data is None:
            _LOGGER.warning("Device %s not found in coordinator data", self._device.id)
            return

        new_value = str(data.device.programming.prog_type)
        if new_value is None or self.native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: object) -> bool:
        if data is None:
            return False
        # Safe attribute access with getattr (coordinator data model has .device.programming.prog_type)
        device = getattr(data, "device", {})
        programming = getattr(device, "programming", {})
        return getattr(programming, "prog_type", None) is not None
