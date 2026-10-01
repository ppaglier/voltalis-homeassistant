from custom_components.voltalis.lib.application.energy_contracts.queries.get_energy_contract_kwh_current_price_query import (  # noqa: E501
    GetEnergyContractKwhCurrentPriceQuery,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_tariff_enum import (
    EnergyContractCurrentTariffEnum,
)


class GetEnergyContractKwhCurrentPriceHandler:
    """Handler to get the current kWh cost of the energy contract."""

    async def handle(self, query: GetEnergyContractKwhCurrentPriceQuery) -> float | None:
        """Handle the request to get the current mode of the energy contract."""

        if query.current_mode is EnergyContractCurrentTariffEnum.PEAK:
            return query.peak_kwh_cost
        if query.current_mode is EnergyContractCurrentTariffEnum.OFF_PEAK:
            return query.off_peak_kwh_cost
        return query.base_kwh_cost
