import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinatorData
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceConsumptionSensor(VoltalisEntity, SensorEntity):
    """References the consumption of a device."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_translation_key = "device_consumption"
    _unique_id_suffix = "device_consumption"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        data = self.coordinator.data.get(self._device.id)
        if data is None:
            _LOGGER.warning("Device %s not found in coordinator data", self._device.id)
            return

        new_value = data.consumption
        if new_value is None or self.native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: VoltalisCoordinatorData) -> bool:
        return data.consumption is not None
