from logging import Logger

from custom_components.voltalis.lib.application.energy_contracts.queries.get_energy_contract_current_kwh_cost_query import (  # noqa: E501
    GetEnergyContractCurrentKwCostQuery,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_mode_enum import (
    EnergyContractCurrentModeEnum,
)


class GetEnergyContractCurrentKwhCostHandler:
    """Handler to get the current kWh cost of the energy contract."""

    async def handle(self, query: GetEnergyContractCurrentKwCostQuery) -> float | None:
        """Handle the request to get the current mode of the energy contract."""

        if query.current_mode is EnergyContractCurrentModeEnum.PEAK:
            return query.peak_kwh_cost
        if query.current_mode is EnergyContractCurrentModeEnum.OFFPEAK:
            return query.offpeak_kwh_cost
        return query.base_kwh_cost
