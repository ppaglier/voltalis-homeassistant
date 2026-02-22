from datetime import time

from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel
from custom_components.voltalis.lib.domain.shared.range_model import RangeModel


class GetEnergyContractCurrentModeQuery(CustomModel):
    """Query to get the current mode of an energy contract."""

    type: EnergyContractTypeEnum
    offpeak_hours: list[RangeModel[time]]
