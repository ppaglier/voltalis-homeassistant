from datetime import time

from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel
from custom_components.voltalis.lib.domain.shared.range_model import RangeModel


class GetEnergyContractCurrentTariffQuery(CustomModel):
    """Query to get the current tariff of an energy contract."""

    type: EnergyContractTypeEnum
    off_peak_hours: list[RangeModel[time]]
