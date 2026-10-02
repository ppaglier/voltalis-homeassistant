from datetime import datetime

from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class EnergyRecord(CustomModel):
    """Class to represent a energy record (in Wh)"""

    timestamp: datetime
    total: float
    peak: float | None = None
    off_peak: float | None = None


class DeviceEnergy(CustomModel):
    """Class to represent Voltalis devices energy"""

    daily_energy_records: list[EnergyRecord]
