from custom_components.voltalis.lib.domain.energy_contracts.live_power import LivePower
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class GetLivePowerHandler:
    """Handler to get the live consumption."""

    def __init__(
        self,
        *,
        voltalis_provider: VoltalisProvider,
    ):
        self.__voltalis_provider = voltalis_provider

    async def handle(self) -> LivePower:
        """Handle the request to get the live consumption."""

        result = await self.__voltalis_provider.get_live_power()
        return result
