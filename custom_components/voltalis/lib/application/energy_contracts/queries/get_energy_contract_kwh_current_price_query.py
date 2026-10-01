from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_tariff_enum import (
    EnergyContractCurrentTariffEnum,
)
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class GetEnergyContractKwhCurrentPriceQuery(CustomModel):
    """Query to get the current kWh price of the energy contract."""

    current_mode: EnergyContractCurrentTariffEnum

    base_kwh_cost: float | None
    peak_kwh_cost: float | None
    offpeak_kwh_cost: float | None
