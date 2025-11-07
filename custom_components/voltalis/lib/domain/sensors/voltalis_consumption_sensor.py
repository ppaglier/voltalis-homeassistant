from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity


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
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        return UnitOfEnergy.KILO_WATT_HOUR

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("refresh")

        device_info: FlashbirdDeviceInfo = self.coordinator.data
        new_value = device_info.get_first_smartkey_battery()
        if new_value is not None:
            if self.native_value != new_value:
                self._attr_native_value = new_value
                self.async_write_ha_state()
