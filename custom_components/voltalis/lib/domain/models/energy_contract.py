from datetime import time
from enum import StrEnum

from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.range_model import RangeModel


class VoltalisEnergyContractType(StrEnum):
    """Enum to represent the type of Voltalis energy contract"""

    BASE = "base"
    PEAK_OFFPEAK = "peak_offpeak"


class VoltalisEnergyContractPrices(CustomModel):
    """Class to represent the prices of a Voltalis energy contract"""

    subscription: float

    kwh_base: float | None = None

    kwh_peak: float | None = None
    kwh_offpeak: float | None = None


class VoltalisEnergyContract(CustomModel):
    """Class to represent a Voltalis energy contract"""

    id: int
    company_name: str
    name: str
    subscribed_power: int
    type: VoltalisEnergyContractType

    prices: VoltalisEnergyContractPrices

    peak_hours: list[RangeModel[time]]
    offpeak_hours: list[RangeModel[time]]
