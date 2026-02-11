from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider
from custom_components.voltalis.lib.domain.voltalis_programs_management.programs.voltalis_program import VoltalisProgram


class GetProgramsHandler:
    """Handler to get the programs."""

    def __init__(
        self,
        *,
        voltalis_provider: VoltalisProvider,
    ):
        self._voltalis_provider = voltalis_provider

    async def handle(self) -> dict[int, VoltalisProgram]:
        """Handle the request to get the programs."""

        result = await self._voltalis_provider.get_programs()
        return result
