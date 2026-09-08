from typing import Literal

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy
from homeassistant.core import callback
from propcache.api import cached_property

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.helpers.is_in_time_range import is_in_time_range


class VoltalisEnergyContractDailyConsumptionSensor(VoltalisEnergyContractEntity, SensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """Sensor entity to represent near real-time consumption for a Voltalis energy contract."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        energy_contract: EnergyContract,
        sensor_type: Literal["peak", "offpeak"] | None,
    ) -> None:
        """Initialize the sensor entity."""

        self._attr_translation_key = "daily_consumption_" + sensor_type if sensor_type else "daily_consumption"
        self._unique_id_suffix = "daily_consumption_" + sensor_type if sensor_type else "daily_consumption"
        super().__init__(
            entry, energy_contract, entry.runtime_data.voltalis_home_assistant_module.live_consumption_coordinator
        )

        self.__sensor_type_hours = (
            energy_contract.peak_hours if sensor_type == "peak" else energy_contract.offpeak_hours
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        devices_data = self._voltalis_module.device_daily_consumption_coordinator.data

        new_value = sum(
            [
                consumption
                for device_data in devices_data.values()
                for (time, consumption) in device_data.daily_consumption_records
                if any(is_in_time_range(time_range, time) for time_range in self.__sensor_type_hours)
            ],
            0.0,
        )
        if self.native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    @cached_property
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Return if the entity is available."""
        data = self.coordinator.data.get(0)
        if data is None:
            return False
        return self.coordinator.last_update_success and self._is_available_from_data(data)

    def _is_available_from_data(self, data: float) -> bool:
        return True
