from datetime import datetime

from pydantic import Field

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisConsumptionDtoDevice(CustomModel):
    """Class to represent a Voltalis device consumption DTO"""

    step_timestamp_on_site: datetime = Field(alias="stepTimestampOnSite")
    total_consumption_in_wh: float = Field(alias="totalConsumptionInWh")


class VoltalisConsumptionDto(CustomModel):
    """Docstring pour VoltalisConsumption"""

    per_appliance: dict[int, list[VoltalisConsumptionDtoDevice]] = Field(alias="perAppliance")
