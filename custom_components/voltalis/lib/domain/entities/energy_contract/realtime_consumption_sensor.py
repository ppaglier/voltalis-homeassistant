import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfPower
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.lib.domain.models.energy_contract import VoltalisEnergyContract

_LOGGER = logging.getLogger(__name__)


class VoltalisEnergyContractRealtimeConsumptionSensor(VoltalisEnergyContractEntity, SensorEntity):
    """References the real-time consumption of a device."""

    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_translation_key = "device_realtime_consumption"
    _unique_id_suffix = "device_realtime_consumption"

    def __init__(self, entry: VoltalisConfigEntry, energy_contract: VoltalisEnergyContract) -> None:
        """Initialize the sensor entity."""
        super().__init__(entry, energy_contract, entry.runtime_data.coordinators.realtime_consumption)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        realtime_consumption = self._coordinators.realtime_consumption.data.get(0, None)
        if realtime_consumption is None:
            _LOGGER.warning("Realtime consumption data is None")
            return

        new_value = realtime_consumption
        if self.native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: float) -> bool:
        return True
