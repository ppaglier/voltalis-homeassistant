from typing import Literal

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy
from homeassistant.core import callback

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract


class VoltalisEnergyContractKwhPriceSensor(VoltalisEnergyContractEntity, SensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """Sensor entity for Voltalis energy contract kWh price."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"
    _attr_icon = "mdi:currency-eur"

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        energy_contract: EnergyContract,
        sensor_type: Literal["peak", "off-peak"] | None,
    ) -> None:
        """Initialize the energy contract kWh price sensor."""
        self._attr_translation_key = (
            f"energy_contract_kwh_{sensor_type}_price" if sensor_type is not None else "energy_contract_kwh_price"
        )
        super().__init__(
            entry, energy_contract, entry.runtime_data.voltalis_home_assistant_module.energy_contract_coordinator
        )
        self.__sensor_type = sensor_type

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        energy_contract = self._voltalis_module.energy_contract_coordinator.data.get(self._energy_contract.id)
        if energy_contract is None:
            self._voltalis_module.logger.warning("Energy contract with id %s is None", self._energy_contract.id)
            return

        new_value = (
            energy_contract.prices.kwh_base
            if self.__sensor_type is None
            else energy_contract.prices.kwh_off_peak
            if self.__sensor_type == "off-peak"
            else energy_contract.prices.kwh_peak
        )
        if new_value is None or self._attr_native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: EnergyContract) -> bool:
        if self.__sensor_type is None:
            return data.prices.kwh_base is not None
        if self.__sensor_type == "peak":
            return data.prices.kwh_peak is not None
        if self.__sensor_type == "off-peak":
            return data.prices.kwh_off_peak is not None
        return False
