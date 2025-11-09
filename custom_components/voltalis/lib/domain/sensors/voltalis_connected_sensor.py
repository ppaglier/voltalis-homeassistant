import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class VoltalisConnectedSensor(VoltalisEntity, BinarySensorEntity):
    """References the connected of a device."""

    @property
    def translation_key(self) -> str:
        return "connected"

    @property
    def icon(self) -> str:
        return "mdi:wifi"

    @property
    def device_class(self) -> BinarySensorDeviceClass:
        return BinarySensorDeviceClass.CONNECTIVITY

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("refresh VoltalisConnectedSensor")

        data = self.coordinator.data.get(self._device.id)
        if data is None:
            _LOGGER.warning("Device %s not found in coordinator data", self._device.id)
            return

        new_value = data.status
        _LOGGER.debug(
            "Updating VoltalisConnectedSensor (%s): old=%s new=%s",
            self._device.name,
            self.is_on,
            new_value,
        )
        if new_value is None or self.is_on == new_value:
            return

        self._attr_is_on = new_value
        self.async_write_ha_state()
