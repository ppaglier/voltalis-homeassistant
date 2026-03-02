from datetime import date, time

from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel
from custom_components.voltalis.lib.domain.shared.range_model import RangeModel


class EnergyContractPrices(CustomModel):
    """Class to represent the prices of an energy contract"""

    subscription: float

    kwh_base: float | None = None

    kwh_peak: float | None = None
    kwh_offpeak: float | None = None


class EnergyContract(CustomModel):
    """Class to represent an energy contract"""

    id: int
    subscriber_id: int
    company_name: str
    name: str
    subscribed_power: int
    type: EnergyContractTypeEnum
    end_date: date | None = None

    prices: EnergyContractPrices

    peak_hours: list[RangeModel[time]]
    offpeak_hours: list[RangeModel[time]]
