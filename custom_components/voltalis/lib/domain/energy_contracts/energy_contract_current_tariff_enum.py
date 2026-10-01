from enum import StrEnum


class EnergyContractCurrentTariffEnum(StrEnum):
    """Voltalis energy contract current mode options."""

    BASE = "base"
    PEAK = "peak"
    OFFPEAK = "offpeak"
