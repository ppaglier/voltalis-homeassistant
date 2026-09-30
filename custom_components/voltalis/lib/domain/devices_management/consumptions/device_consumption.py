from datetime import datetime

from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class ConsumptionRecord(CustomModel):
    """Class to represent a consumption record"""

    timestamp: datetime
    total_consumption_in_wh: float
    peak_consumption_in_wh: float | None = None
    offpeak_consumption_in_wh: float | None = None


class DeviceConsumption(CustomModel):
    """Class to represent Voltalis devices consumption"""

    daily_consumption_records: list[ConsumptionRecord]
