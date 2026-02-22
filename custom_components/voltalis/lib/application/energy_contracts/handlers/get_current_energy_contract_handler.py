from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class GetCurrentEnergyContractHandler:
    """Handler to get the current energy contract."""

    def __init__(
        self,
        *,
        date_provider: DateProvider,
        voltalis_provider: VoltalisProvider,
    ):
        self.__date_provider = date_provider
        self.__voltalis_provider = voltalis_provider

    async def handle(self) -> EnergyContract | None:
        """Handle the request to get the current energy contract."""

        energy_contracts = await self.__voltalis_provider.get_energy_contracts()

        now = self.__date_provider.get_now().date()
        for energy_contract in energy_contracts.values():
            if energy_contract.end_date is None or now <= energy_contract.end_date:
                return energy_contract

        return None
