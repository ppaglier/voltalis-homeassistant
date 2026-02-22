from custom_components.voltalis.lib.domain.programs_management.programs.program import Program
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class SetProgramHandler:
    """Handler to set the program."""

    def __init__(
        self,
        *,
        voltalis_provider: VoltalisProvider,
    ):
        self.__voltalis_provider = voltalis_provider

    async def handle(
        self,
        *,
        new_program: Program | None,
        old_program: Program | None = None,
    ) -> None:
        """Handle the request to set the program."""

        if old_program is not None:
            old_program.enabled = False
            await self.__voltalis_provider.toggle_program(old_program)

        if new_program is not None:
            new_program.enabled = True
            await self.__voltalis_provider.toggle_program(new_program)
