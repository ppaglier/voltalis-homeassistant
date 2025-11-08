import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


class VoltalisConsumptionSensor(VoltalisEntity, SensorEntity):
    """References the consumption of a device."""

    @property
    def icon(self) -> str:
        return "mdi:lightning-bolt"

    @property
    def device_class(self) -> SensorDeviceClass:
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self) -> SensorStateClass:
        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_unit_of_measurement(self) -> str:
        return UnitOfEnergy.WATT_HOUR

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("refresh VoltalisConsumptionSensor")

        data = self.coordinator.data.get(self._device.id)
        if data is None:
            _LOGGER.warning("Device %s not found in coordinator data", self._device.id)
            return

        new_value = data.consumption
        _LOGGER.debug(
            "Updating VoltalisConsumptionSensor (%s): old=%s new=%s",
            self._device.name,
            self.native_value,
            new_value,
        )
        if new_value is None or self.native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()
