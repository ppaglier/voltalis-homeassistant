import logging

from homeassistant.components.sensor import SensorEntity

from custom_components.voltalis.lib.domain.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.models.energy_contract import VoltalisEnergyContract

_LOGGER = logging.getLogger(__name__)


class VoltalisEnergyContractInfoSensor(VoltalisEnergyContractEntity, SensorEntity):
    """Sensor entity for Voltalis energy contract information."""

    _attr_translation_key = "energy_contract_info"
    _attr_icon = "mdi:file-document-outline"

    def __init__(self, entry: VoltalisConfigEntry, energy_contract: VoltalisEnergyContract) -> None:
        """Initialize the energy contract info sensor."""
        super().__init__(entry, energy_contract, entry.runtime_data.coordinators.energy_contract)

    def _update_state(self) -> None:
        """Update the state of the sensor."""
        # The native value is the contract name
        self._attr_native_value = self._energy_contract.name

        # Extra state attributes contain all the contract details
        self._attr_extra_state_attributes = {
            "contract_id": self._energy_contract.id,
            "company_name": self._energy_contract.company_name,
            "subscribed_power": self._energy_contract.subscribed_power,
            # "is_peak_offpeak_contract": self._energy_contract.is_peak_offpeak_contract,
            # "is_default": self._energy_contract.is_default,
            # "start_date": self._energy_contract.start_date,
            # "end_date": self._energy_contract.end_date,
            # "subscription_base_price": self._energy_contract.subscription_base_price,
            # "subscription_peak_offpeak_base_price": self._energy_contract.subscription_peak_offpeak_base_price,
            # "kwh_base_price": self._energy_contract.kwh_base_price,
            # "kwh_peak_hour_price": self._energy_contract.kwh_peak_hour_price,
            # "kwh_offpeak_hour_price": self._energy_contract.kwh_offpeak_hour_price,
            # "peak_hours": [{"from": hour.from_time, "to": hour.to_time} for hour in self._energy_contract.peak_hours],
            # "offpeak_hours": [
            #     {"from": hour.from_time, "to": hour.to_time} for hour in self._energy_contract.offpeak_hours
            # ],
        }

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: VoltalisEnergyContract) -> bool:
        return True
