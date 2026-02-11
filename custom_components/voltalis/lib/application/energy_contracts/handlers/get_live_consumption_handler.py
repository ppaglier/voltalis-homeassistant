from custom_components.voltalis.lib.domain.energy_contracts.live_consumption import VoltalisLiveConsumption
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class GetLiveConsumptionHandler:
    """Handler to get the live consumption."""

    def __init__(
        self,
        *,
        voltalis_provider: VoltalisProvider,
    ):
        self._voltalis_provider = voltalis_provider

    async def handle(self) -> VoltalisLiveConsumption:
        """Handle the request to get the live consumption."""

        result = await self._voltalis_provider.get_live_consumption()
        return result
