from typing import Annotated

from pydantic import Field

from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class VoltalisRealtimeConsumptionDtoConsumption(CustomModel):
    """Class to represent a Voltalis device consumption DTO"""

    total_consumption_in_wh: Annotated[float, Field(alias="totalConsumptionInWh")]


class VoltalisRealtimeConsumptionDto(CustomModel):
    """Docstring pour VoltalisConsumption"""

    consumptions: list[VoltalisRealtimeConsumptionDtoConsumption]
