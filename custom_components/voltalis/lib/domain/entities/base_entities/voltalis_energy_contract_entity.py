from typing import Any

from homeassistant.helpers.entity import DeviceInfo

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.base_entities.voltalis_base_entity import VoltalisBaseEntity
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.models.energy_contract import VoltalisEnergyContract


class VoltalisEnergyContractEntity(VoltalisBaseEntity):
    """Base class for Voltalis energy contract entities."""

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        energy_contract: VoltalisEnergyContract,
        coordinator: BaseVoltalisCoordinator[dict[int, Any]],
    ) -> None:
        """Initialize the energy contract entity."""
        super().__init__(entry, coordinator)

        self._energy_contract = energy_contract

        unique_id = str(energy_contract.id)

        # Unique id for Home Assistant
        self._attr_unique_id = f"{unique_id}_{self._unique_id_suffix}"
        contract_model = self.__get_energy_contract_model()

        self._attr_device_info: DeviceInfo = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=contract_model,
            manufacturer=energy_contract.company_name,
            model=contract_model,
        )

    @property
    def unique_internal_name(self) -> str:
        """Return a unique internal name for the entity."""
        return f"{self._energy_contract.name.lower()}_{self._attr_unique_id}"

    @property
    def has_entity_name(self) -> bool:
        return True

    @property
    def device_info(self) -> DeviceInfo:
        return self._attr_device_info

    def __get_energy_contract_model(self) -> str:
        """Return the translation key for the device model."""

        contract_name = self._energy_contract.name
        contract_power = f"{self._energy_contract.subscribed_power} KVA"
        contract_type = self._energy_contract.type.value

        return f"{contract_name} | {contract_power} | {contract_type}"

    # ------------------------------------------------------------------
    # Availability handling
    # ------------------------------------------------------------------
    @property
    def available(self) -> bool:
        """Return True if entity is available.

        We consider an entity available only if:
        - The last coordinator update succeeded AND
        - Energy contract data exists for this entity AND
        - Subclass-specific data is present.
        """
        data = self.coordinator.data.get(self._energy_contract.id)
        if data is None:
            return False
        return self.coordinator.last_update_success and self._is_available_from_data(data)
