import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice
from custom_components.voltalis.lib.domain.voltalis_device_entity import VoltalisDeviceEntity

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceConsumptionSensor(VoltalisDeviceEntity, SensorEntity):
    """References the consumption of a device."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_translation_key = "device_consumption"
    _unique_id_suffix = "device_consumption"

    def __init__(self, entry: VoltalisConfigEntry, device: VoltalisDevice) -> None:
        """Initialize the sensor entity."""
        super().__init__(entry, device, entry.runtime_data.coordinators.device_consumption)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        device_consumption = self._coordinators.device_consumption.data.get(self._device.id)
        if device_consumption is None:
            _LOGGER.warning("Consumption data for device %s is None", self._device.id)
            return

        new_value = device_consumption
        if new_value is None or self.native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: float) -> bool:
        return True
