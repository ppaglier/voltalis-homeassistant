from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider
from custom_components.voltalis.lib.domain.voltalis_programs_management.programs.voltalis_program import VoltalisProgram


class SetCurrentProgramHandler:
    """Handler to set the current program."""

    def __init__(
        self,
        *,
        voltalis_provider: VoltalisProvider,
    ):
        self._voltalis_provider = voltalis_provider

    async def handle(
        self,
        *,
        new_program: VoltalisProgram | None,
        old_program: VoltalisProgram | None = None,
    ) -> None:
        """Handle the request to set the current program."""

        if old_program is not None:
            old_program.enabled = False
            await self._voltalis_provider.toggle_program(old_program)

        if new_program is not None:
            new_program.enabled = True
            await self._voltalis_provider.toggle_program(new_program)
