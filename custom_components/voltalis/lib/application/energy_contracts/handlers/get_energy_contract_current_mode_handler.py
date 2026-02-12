from custom_components.voltalis.lib.application.energy_contracts.queries.get_energy_contract_current_mode_query import (
    GetEnergyContractCurrentModeQuery,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_mode_enum import (
    EnergyContractCurrentModeEnum,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_service import EnergyContractService
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider


class GetEnergyContractCurrentModeHandler:
    """Handler to get the current mode of the energy contract."""

    def __init__(
        self,
        *,
        date_provider: DateProvider,
    ):
        self.__energy_contract_service = EnergyContractService(date_provider=date_provider)

    async def handle(self, query: GetEnergyContractCurrentModeQuery) -> EnergyContractCurrentModeEnum:
        """Handle the request to get the current mode of the energy contract."""

        return self.__energy_contract_service.get_current_mode(type=query.type, offpeak_hours=query.offpeak_hours)
