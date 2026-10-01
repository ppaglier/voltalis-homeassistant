from typing import Literal

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfEnergy
from homeassistant.core import callback
from propcache.api import cached_property

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract


class VoltalisEnergyContractDailyConsumptionSensor(VoltalisEnergyContractEntity, SensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """Sensor entity to represent near real-time consumption for a Voltalis energy contract."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = None
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        energy_contract: EnergyContract,
        sensor_type: Literal["peak", "off-peak"] | None,
    ) -> None:
        """Initialize the sensor entity."""

        suffix = f"_{sensor_type}" if sensor_type else ""
        self.__sensor_type = sensor_type
        self._attr_translation_key = f"daily_consumption{suffix}"
        self._statistic_id = f"voltalis:contract_{entry.entry_id.lower()}_{energy_contract.id}_energy{suffix}"
        super().__init__(
            entry,
            energy_contract,
            entry.runtime_data.voltalis_home_assistant_module.device_daily_consumption_coordinator,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        devices_data = self._voltalis_module.device_daily_consumption_coordinator.data
        new_value = sum(
            [
                (
                    record.total_consumption_in_wh
                    if self.__sensor_type is None
                    else (record.peak_consumption_in_wh or 0.0)
                    if self.__sensor_type == "peak"
                    else (record.off_peak_consumption_in_wh or 0.0)
                )
                for device_data in devices_data.values()
                for record in device_data.daily_consumption_records
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
        if not self.coordinator.data:
            return False
        return self.coordinator.last_update_success

    def _is_available_from_data(self, data: float) -> bool:
        return True
