from enum import StrEnum


class EnergyContractCurrentModeEnum(StrEnum):
    """Voltalis energy contract current mode options."""

    BASE = "base"
    PEAK = "peak"
    OFFPEAK = "offpeak"
