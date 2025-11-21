from homeassistant.helpers.entity import DeviceInfo, Entity

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator
from custom_components.voltalis.lib.domain.models.subscriber_contract import VoltalisSubscriberContract


class VoltalisContractEntity(Entity):
    """Base class for Voltalis contract entities (independent from VoltalisEntity for devices)."""

    _attr_has_entity_name = True
    _unique_id_suffix: str = ""

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        contract: VoltalisSubscriberContract,
    ) -> None:
        """Initialize the contract entity."""
        self._entry = entry
        self._contract = contract
        self._coordinator = entry.runtime_data.coordinator

        if len(self._unique_id_suffix) == 0:
            raise ValueError("Unique ID suffix must be defined in subclass.")

        # Unique id for Home Assistant
        unique_id = f"contract_{contract.id}"
        self._attr_unique_id = f"{unique_id}_{self._unique_id_suffix}"

        # Create device info for the contract
        self._attr_device_info: DeviceInfo = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=f"{contract.company_name} - {contract.name}",
            manufacturer="Voltalis",
            model="Subscriber Contract",
        )

    @property
    def coordinator(self) -> VoltalisCoordinator:
        """Return the coordinator."""
        return self._coordinator

    @property
    def unique_internal_name(self) -> str:
        """Return a unique internal name for the entity."""
        return f"contract_{self._contract.id}_{self._attr_unique_id}"

    @property
    def has_entity_name(self) -> bool:
        return True

    @property
    def device_info(self) -> DeviceInfo:
        return self._attr_device_info

    @property
    def available(self) -> bool:
        """Return True if entity is available.
        
        Contract entities are always available once loaded since they don't update frequently.
        """
        return len(self._coordinator.contracts) > 0
