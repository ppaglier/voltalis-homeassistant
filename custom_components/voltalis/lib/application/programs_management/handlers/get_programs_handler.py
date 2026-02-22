from custom_components.voltalis.lib.domain.programs_management.programs.program import Program
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class GetProgramsHandler:
    """Handler to get the programs."""

    def __init__(
        self,
        *,
        voltalis_provider: VoltalisProvider,
    ):
        self.__voltalis_provider = voltalis_provider

    async def handle(self) -> dict[int, Program]:
        """Handle the request to get the programs."""

        result = await self.__voltalis_provider.get_programs()
        return result
