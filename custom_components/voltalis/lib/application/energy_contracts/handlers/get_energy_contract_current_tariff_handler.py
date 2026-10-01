from custom_components.voltalis.lib.application.energy_contracts.queries.get_energy_contract_current_tariff_query import (  # noqa: E501
    GetEnergyContractCurrentTariffQuery,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_tariff_enum import (
    EnergyContractCurrentTariffEnum,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_service import EnergyContractService
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider


class GetEnergyContractCurrentTariffHandler:
    """Handler to get the current tariff of the energy contract."""

    def __init__(
        self,
        *,
        date_provider: DateProvider,
    ):
        self.__energy_contract_service = EnergyContractService(date_provider=date_provider)

    async def handle(self, query: GetEnergyContractCurrentTariffQuery) -> EnergyContractCurrentTariffEnum:
        """Handle the request to get the current mode of the energy contract."""

        return self.__energy_contract_service.get_current_mode(
            contract_type=query.type, off_peak_hours=query.off_peak_hours
        )
