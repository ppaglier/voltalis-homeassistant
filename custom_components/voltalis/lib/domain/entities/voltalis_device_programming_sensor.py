from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.coordinators.coordinator import VoltalisCoordinatorData
from custom_components.voltalis.lib.domain.models.device import VoltalisDeviceProgTypeEnum
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceProgrammingSensor(VoltalisEntity, SensorEntity):
    """Sensor for programming of devices (manual, default, user, quick)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "device_programming"
    _attr_options = [option for option in VoltalisDeviceProgTypeEnum]
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _unique_id_suffix = "device_programming"

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
    def _is_available_from_data(self, data: VoltalisCoordinatorData) -> bool:
        return data.device.programming.prog_type is not None
