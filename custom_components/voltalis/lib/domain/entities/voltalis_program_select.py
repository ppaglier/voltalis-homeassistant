from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_base_entity import VoltalisBaseEntity
from custom_components.voltalis.lib.domain.models.program import VoltalisProgram

_LOGGER = logging.getLogger(__name__)


class VoltalisProgramSelect(VoltalisBaseEntity, SelectEntity):
    """Select entity for Voltalis program."""

    _attr_translation_key = "program_select"
    _attr_icon = "mdi:calendar-clock"
    _unique_id_suffix = "program_select"

    __none_program_option = "internal_program-none"

    def __init__(self, entry: VoltalisConfigEntry) -> None:
        """Initialize the program select entity."""

        super().__init__(entry, entry.runtime_data.coordinators.programs)

        # Unique id for Home Assistant
        self._attr_unique_id = f"programs_{self._unique_id_suffix}"
        self.unique_id = self._attr_unique_id

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
        """Return if entity is available."""
        data = self.coordinator.data
        return data is not None and self.coordinator.last_update_success

    @property
    def __programs(self) -> dict[str, VoltalisProgram | None]:
        """Get the available programs mapped by their name."""
        if self._coordinators.programs.data is None:
            return {}

        programs: dict[str, VoltalisProgram | None] = {
            self.__none_program_option: None,
        }
        for program in self._coordinators.programs.data.values():
            if program.name not in programs:
                programs[program.name] = program

        return programs

    def _get_program_by_name(self, name: str) -> VoltalisProgram | None:
        """Get a program by its name."""
        if name == self.__none_program_option:
            return None

        return self.__programs.get(name, None)

    @property
    def _current_program(self) -> VoltalisProgram | None:
        """Get the currently selected program."""
        if self.current_option is None:
            return None
        return self._get_program_by_name(self.current_option)

    @property
    def options(self) -> list[str]:
        """Return the list of available program options."""
        return list(self.__programs.keys())

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        enabled_programs = [program for program in self.__programs.values() if program and program.enabled]
        if len(enabled_programs) > 0:
            if len(enabled_programs) > 1:
                _LOGGER.warning("More than one program is enabled (%s)", enabled_programs)
            self._attr_current_option = enabled_programs[0].name
        else:
            self._attr_current_option = self.__none_program_option
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected program mode."""

        old_program = self._current_program
        new_program = self._get_program_by_name(option)

        if old_program and new_program and old_program.id == new_program.id:
            return

        await self._coordinators.programs.set_program(
            new_program=new_program,
            old_program=old_program,
        )
        self._attr_current_option = new_program.name if new_program else self.__none_program_option
        await self.coordinator.async_request_refresh()
