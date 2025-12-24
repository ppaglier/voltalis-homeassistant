import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import EntityCategory
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.base_entities.voltalis_device_entity import VoltalisDeviceEntity
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinators.device import VoltalisDeviceCoordinatorData
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth, VoltalisHealthStatusEnum

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceConnectedSensor(VoltalisDeviceEntity, SensorEntity):
    """References the connected of a device."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "device_connected"
    _attr_options = [option for option in VoltalisHealthStatusEnum]
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _unique_id_suffix = "device_connected"

    def __init__(self, entry: VoltalisConfigEntry, device: VoltalisDeviceCoordinatorData) -> None:
        """Initialize the sensor entity."""
        super().__init__(entry, device, entry.runtime_data.coordinators.device_health)

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        if self.native_value is None:
            return "mdi:minus-network-outline"
        if self.native_value == VoltalisHealthStatusEnum.TEST_IN_PROGRESS:
            return "mdi:help-network-outline"
        if self.native_value == VoltalisHealthStatusEnum.OK:
            return "mdi:check-network-outline"
        return "mdi:close-network-outline"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        device_health = self._coordinators.device_health.data.get(self._device.id)
        if device_health is None:
            _LOGGER.warning("Health data for device %s is None", self._device.id)
            return

        new_value = device_health.status
        if new_value is None or self._attr_native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: VoltalisDeviceHealth) -> bool:
        return True
