from typing import Any

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_base_entity import VoltalisBaseEntity


class VoltalisProgramsEntity(VoltalisBaseEntity):
    """Base class for Voltalis programs entities tied to a specific device."""

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        coordinator: BaseVoltalisCoordinator[dict[int, Any]],
    ) -> None:
        """Initialize the program entity."""
        super().__init__(entry, coordinator)

        # Unique id for Home Assistant
        self._attr_unique_id = f"programs_{self._unique_id_suffix}"

    @property
    def unique_internal_name(self) -> str:
        """Return a unique internal name for the entity."""
        return f"programs_{self._attr_unique_id}"

    @property
    def has_entity_name(self) -> bool:
        return True

    # ------------------------------------------------------------------
    # Availability handling
    # ------------------------------------------------------------------
    @property
    def available(self) -> bool:
        """Return True if entity is available.

        We consider an entity available only if:
        - The last coordinator update succeeded AND
        - Device data exists for this entity AND
        - Subclass-specific data (consumption/status) is present.
        """
        data = self.coordinator.data
        if data is None:
            return False
        return self.coordinator.last_update_success and self._is_available_from_data(data)
