from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_current_mode_enum import (
    EnergyContractCurrentModeEnum,
)
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class GetEnergyContractCurrentKwCostQuery(CustomModel):
    """Query to get the current kWh cost of the energy contract."""

    current_mode: EnergyContractCurrentModeEnum

    base_kwh_cost: float | None
    peak_kwh_cost: float | None
    offpeak_kwh_cost: float | None
