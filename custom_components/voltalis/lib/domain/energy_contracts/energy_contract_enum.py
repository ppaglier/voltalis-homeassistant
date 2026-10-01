from enum import StrEnum


class EnergyContractTypeEnum(StrEnum):
    """Enum to represent the type of energy contract"""

    BASE = "base"
    PEAK_OFF_PEAK = "peak_off-peak"
