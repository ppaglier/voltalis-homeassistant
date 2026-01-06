from __future__ import annotations

import logging
from typing import cast

from homeassistant.components.select import SelectEntity
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_programs_entity import VoltalisProgramsEntity
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice
from custom_components.voltalis.lib.domain.models.program import VoltalisProgram

_LOGGER = logging.getLogger(__name__)


class VoltalisProgramSelect(VoltalisProgramsEntity, SelectEntity):
    """Select entity for Voltalis program."""

    _attr_translation_key = "program_select"
    _unique_id_suffix = "program_select"

    def __init__(self, entry: VoltalisConfigEntry) -> None:
        """Initialize the program select entity."""
        super().__init__(entry, entry.runtime_data.coordinators.programs)

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        return "mdi:playlist-edit"

    @property
    def options(self) -> list[str]:
        """Return the list of available program options."""
        data = cast(dict[int, VoltalisProgram] | None, self.coordinator.data)
        if data is None:
            return []
        return [program.name for program in data.values()]

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        self._attr_current_option = None
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected program mode."""

        pass

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: VoltalisDevice) -> bool:
        return True
