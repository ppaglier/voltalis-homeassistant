from datetime import datetime

from pydantic import Field

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisRealtimeConsumptionDtoConsumption(CustomModel):
    """Class to represent a Voltalis device consumption DTO"""

    step_timestamp_in_utc: datetime = Field(alias="stepTimestampInUtc")
    total_consumption_in_wh: float = Field(alias="totalConsumptionInWh")


class VoltalisRealtimeConsumptionDto(CustomModel):
    """Docstring pour VoltalisConsumption"""

    consumptions: list[VoltalisRealtimeConsumptionDtoConsumption]
