from datetime import timedelta

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.voltalis_programs_management.programs.program import Program


class VoltalisProgramCoordinator(BaseVoltalisCoordinator[dict[int, Program]]):
    """Coordinator to fetch programs from Voltalis API."""

    def __init__(
        self,
        *,
        entry: VoltalisConfigEntry,
    ) -> None:
        super().__init__(
            "Voltalis Program",
            entry=entry,
            update_interval=timedelta(minutes=1),
        )

    async def set_program(
        self,
        *,
        new_program: Program | None,
        old_program: Program | None = None,
    ) -> None:
        """Set the active program."""

        await self._voltalis_module.set_current_program_handler.handle(
            new_program=new_program,
            old_program=old_program,
        )

    async def _get_data(self) -> dict[int, Program]:
        """Fetch updated data from the Voltalis API."""

        # Fetch programs
        result = await self._voltalis_module.get_programs_handler.handle()
        return result
