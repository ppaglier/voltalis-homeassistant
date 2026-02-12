from logging import Logger

from custom_components.voltalis.lib.application.energy_contracts.queries.get_energy_contract_current_kwh_cost_query import (  # noqa: E501
    GetEnergyContractCurrentKwCostQuery,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_mode_enum import (
    EnergyContractCurrentModeEnum,
)


class GetEnergyContractCurrentKwhCostHandler:
    """Handler to get the current kWh cost of the energy contract."""

    def __init__(
        self,
        *,
        logger: Logger,
    ):

        self.__logger = logger

    async def handle(self, query: GetEnergyContractCurrentKwCostQuery) -> float | None:
        """Handle the request to get the current mode of the energy contract."""

        match query.current_mode:
            case EnergyContractCurrentModeEnum.BASE:
                return query.base_kwh_cost
            case EnergyContractCurrentModeEnum.PEAK:
                return query.peak_kwh_cost
            case EnergyContractCurrentModeEnum.OFFPEAK:
                return query.offpeak_kwh_cost
            case _:
                self.__logger.error("Unknown energy contract current mode: %s", query.current_mode)
                return None
