from typing import Any

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator


class VoltalisBaseEntity(CoordinatorEntity[BaseVoltalisCoordinator[dict[int, Any]]]):
    """Base class for all Voltalis entities."""

    _unique_id_suffix: str = ""

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        coordinator: BaseVoltalisCoordinator[dict[int, Any]],
    ) -> None:
        """Initialize the base entity."""
        super().__init__(coordinator)
        self._entry = entry

        if len(self._unique_id_suffix) == 0:
            raise ValueError("Unique ID suffix must be defined in subclass.")

        self._coordinators = entry.runtime_data.coordinators

    # ------------------------------------------------------------------
    # Availability handling
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: Any) -> bool:
        """Check if entity is available based on entity data.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError()
