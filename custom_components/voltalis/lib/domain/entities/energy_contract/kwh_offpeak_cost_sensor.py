import logging

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import CURRENCY_EURO, UnitOfEnergy
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.lib.domain.models.energy_contract import VoltalisEnergyContract

_LOGGER = logging.getLogger(__name__)


class VoltalisEnergyContractKwhOffPeakCostSensor(VoltalisEnergyContractEntity, SensorEntity):
    """Sensor entity for Voltalis energy contract kWh off-peak cost."""

    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = f"{CURRENCY_EURO}/{UnitOfEnergy.KILO_WATT_HOUR}"
    _attr_translation_key = "energy_contract_kwh_off_peak_cost"
    _attr_icon = "mdi:currency-eur"
    _unique_id_suffix = "energy_contract_kwh_off_peak_cost"

    def __init__(self, entry: VoltalisConfigEntry, energy_contract: VoltalisEnergyContract) -> None:
        """Initialize the energy contract kWh off-peak cost sensor."""
        super().__init__(entry, energy_contract, entry.runtime_data.coordinators.energy_contract)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        energy_contract = self._coordinators.energy_contract.data.get(self._energy_contract.id)
        if energy_contract is None:
            _LOGGER.warning("Energy contract with id %s is None", self._energy_contract.id)
            return

        new_value = energy_contract.prices.kwh_offpeak
        if new_value is None or self._attr_native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: VoltalisEnergyContract) -> bool:
        return data.prices.kwh_offpeak is not None
