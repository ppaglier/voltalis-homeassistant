import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.models.program import VoltalisProgram, VoltalisProgramTypeEnum

_LOGGER = logging.getLogger(__name__)


class VoltalisProgramCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisProgram]]):
    """Coordinator to fetch programs from Voltalis API."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        voltalis_repository: VoltalisRepository,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(
            "Voltalis Program",
            hass=hass,
            logger=_LOGGER,
            voltalis_repository=voltalis_repository,
            entry=entry,
            update_interval=timedelta(minutes=5),  # Programs don't change often
        )

    async def set_program_state(self, program: VoltalisProgram, enabled: bool) -> None:
        """Set the enabled state of a program."""
        if program.program_type == VoltalisProgramTypeEnum.USER:
            await self._voltalis_repository.set_user_program_state(
                program_id=program.id,
                name=program.name,
                enabled=enabled,
            )
        else:
            await self._voltalis_repository.set_default_program_state(
                program_id=program.id,
                enabled=enabled,
            )

    async def _get_data(self) -> dict[int, VoltalisProgram]:
        """Fetch updated data from the Voltalis API."""
        # For initial fetch, get all programs
        if self.data is None:
            return await self._voltalis_repository.get_programs()

        # For updates, refresh programs based on their type
        updated_programs: dict[int, VoltalisProgram] = {}

        # Update USER programs individually
        for program_id, program in self.data.items():
            if program.program_type == VoltalisProgramTypeEnum.USER:
                try:
                    updated_program = await self._voltalis_repository.get_user_program(program_id)
                    updated_programs[program_id] = updated_program
                except Exception as err:
                    self.logger.warning("Failed to update user program %s: %s", program_id, err)
                    # Keep old data on failure
                    updated_programs[program_id] = program

        # Update DEFAULT programs in batch
        default_programs = await self._voltalis_repository.get_default_programs()
        updated_programs.update(default_programs)

        return updated_programs

