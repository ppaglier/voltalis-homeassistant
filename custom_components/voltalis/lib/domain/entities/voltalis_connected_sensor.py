import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.models.device_health import VoltalisHealthStatusEnum
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)


class VoltalisConnectedSensor(VoltalisEntity, SensorEntity):
    """References the connected of a device."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "connected"
    _attr_options = [option for option in VoltalisHealthStatusEnum]
    _unique_id_suffix = "connected"

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        if self.native_value is None:
            return "mdi:minus-network-outline"
        if self.native_value == VoltalisHealthStatusEnum.TEST_IN_PROGRESS:
            return "mdi:help-network-outline"
        if self.native_value == VoltalisHealthStatusEnum.NOT_OK:
            return "mdi:close-network-outline"
        return "mdi:check-network-outline"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        data = self.coordinator.data.get(self._device.id)
        if data is None:
            _LOGGER.warning("Device %s not found in coordinator data", self._device.id)
            return

        if data.health is None:
            _LOGGER.warning("Health data for device %s is None", self._device.id)
            return

        new_value = data.health.status
        if new_value is None or self._attr_native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: object) -> bool:
        if data is None:
            return False
        health = getattr(data, "health", {})
        return getattr(health, "status", None) is not None
