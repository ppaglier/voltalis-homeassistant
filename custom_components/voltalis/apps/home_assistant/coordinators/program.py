from datetime import timedelta

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.apps.home_assistant.home_assistant_module import VoltalisHomeAssistantModule
from custom_components.voltalis.lib.domain.voltalis_programs_management.programs.voltalis_program import VoltalisProgram


class VoltalisProgramCoordinator(BaseVoltalisCoordinator[dict[int, VoltalisProgram]]):
    """Coordinator to fetch programs from Voltalis API."""

    def __init__(
        self,
        *,
        voltalis_module: VoltalisHomeAssistantModule,
    ) -> None:
        super().__init__(
            "Voltalis Program",
            voltalis_module=voltalis_module,
            update_interval=timedelta(minutes=1),
        )

    async def set_program(
        self,
        *,
        new_program: VoltalisProgram | None,
        old_program: VoltalisProgram | None = None,
    ) -> None:
        """Set the active program."""

        await self._voltalis_module.set_current_program_handler.handle(
            new_program=new_program,
            old_program=old_program,
        )

    async def _get_data(self) -> dict[int, VoltalisProgram]:
        """Fetch updated data from the Voltalis API."""

        # Fetch programs
        result = await self._voltalis_module.get_programs_handler.handle()
        return result
