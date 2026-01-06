import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.voltalis.lib.application.repositories.voltalis_repository import VoltalisRepository
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.models.program import VoltalisProgram

_LOGGER = logging.getLogger(__name__)


class VoltalisProgramCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisProgram]]):
    """Coordinator to fetch programs from Voltalis API."""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        voltalis_repository: VoltalisRepository,
        entry: ConfigEntry,  # ConfigEntry reference used for reauth triggering
    ) -> None:
        super().__init__(
            "Voltalis Program",
            hass=hass,
            logger=_LOGGER,
            voltalis_repository=voltalis_repository,
            entry=entry,
            update_interval=timedelta(minutes=1),
        )

    async def set_program(
        self,
        *,
        new_program: VoltalisProgram | None,
        old_program: VoltalisProgram | None = None,
    ) -> None:
        """Set the active program."""

        if old_program is not None:
            old_program.enabled = False
            await self._voltalis_repository.toggle_program(old_program)

        if new_program is not None:
            new_program.enabled = True
            await self._voltalis_repository.toggle_program(new_program)

    async def _get_data(self) -> dict[int, VoltalisProgram]:
        """Fetch updated data from the Voltalis API."""

        # Fetch programs
        result = await self._voltalis_repository.get_programs()
        return result
