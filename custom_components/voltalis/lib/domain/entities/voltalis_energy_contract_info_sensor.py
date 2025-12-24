import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.models.energy_contract import VoltalisEnergyContract

_LOGGER = logging.getLogger(__name__)


class VoltalisEnergyContractInfoSensor(VoltalisEnergyContractEntity, SensorEntity):
    """Sensor entity for Voltalis energy contract information."""

    _unique_id_suffix = "energy_contract_info"
    _attr_translation_key = "energy_contract_info"
    _attr_icon = "mdi:file-document-outline"

    def __init__(self, entry: VoltalisConfigEntry, energy_contract: VoltalisEnergyContract) -> None:
        """Initialize the energy contract info sensor."""
        super().__init__(entry, energy_contract, entry.runtime_data.coordinators.energy_contract)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        energy_contract = self._coordinators.energy_contract.data.get(self._energy_contract.id)
        if energy_contract is None:
            _LOGGER.warning("Energy contract with id %s is None", self._energy_contract.id)
            return

        self._attr_extra_state_attributes = {
            "contract_id": energy_contract.id,
            "company_name": energy_contract.company_name,
            "subscribed_power": energy_contract.subscribed_power,
            "type": energy_contract.type.value,
            "prices": energy_contract.prices.model_dump_json(),
            # "peak_hours": energy_contract.peak_hours,
            # "offpeak_hours": energy_contract.offpeak_hours,
        }

        new_value = energy_contract.name
        if new_value is None or self._attr_native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: VoltalisEnergyContract) -> bool:
        return True
