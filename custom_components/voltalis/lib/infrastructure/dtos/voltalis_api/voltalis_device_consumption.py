from datetime import datetime
from typing import Annotated

from pydantic import Field

from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class VoltalisConsumptionDtoDevice(CustomModel):
    """Class to represent a Voltalis device consumption DTO"""

    step_timestamp_on_site: Annotated[datetime, Field(alias="stepTimestampOnSite")]
    total_consumption_in_wh: Annotated[float, Field(alias="totalConsumptionInWh")]


class VoltalisConsumptionDto(CustomModel):
    """Docstring pour VoltalisConsumption"""

    per_appliance: Annotated[dict[int, list[VoltalisConsumptionDtoDevice]], Field(alias="perAppliance")]
