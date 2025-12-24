from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinators.device import VoltalisDeviceCoordinatorData
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_device_entity import VoltalisDeviceEntity
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceProgTypeEnum

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceProgrammingSensor(VoltalisDeviceEntity, SensorEntity):
    """Sensor for programming of devices (manual, default, user, quick)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "device_programming"
    _attr_options = [option for option in VoltalisDeviceProgTypeEnum]
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False
    _unique_id_suffix = "device_programming"

    def __init__(self, entry: VoltalisConfigEntry, device: VoltalisDeviceCoordinatorData) -> None:
        """Initialize the sensor entity."""
        super().__init__(entry, device, entry.runtime_data.coordinators.device)

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

        device = self._coordinators.device.data.get(self._device.id)
        if device is None:
            _LOGGER.warning("Device %s not found in coordinator data", self._device.id)
            return

        new_value = str(device.programming.prog_type)
        if new_value is None or self.native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: VoltalisDevice) -> bool:
        return data.programming.prog_type is not None
