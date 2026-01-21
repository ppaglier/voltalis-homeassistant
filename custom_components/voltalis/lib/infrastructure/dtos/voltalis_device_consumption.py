from datetime import datetime

from pydantic import Field

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisConsumptionDtoDevice(CustomModel):
    """Class to represent a Voltalis device consumption DTO"""

    step_timestamp_on_site: datetime = Field(alias="stepTimestampOnSite")
    total_consumption_in_wh: float = Field(alias="totalConsumptionInWh")


class VoltalisConsumptionDtoBreakdownCategorySubCategory(CustomModel):
    """Docstring pour VoltalisConsumptionDtoBreakdownCategorySubCategory"""

    name: str
    total_consumption_in_wh: float = Field(alias="totalConsumptionInWh")


class VoltalisConsumptionDtoBreakdownCategory(CustomModel):
    """Docstring pour VoltalisConsumptionDtoBreakdownCategory"""

    name: str
    subcategories: list[VoltalisConsumptionDtoBreakdownCategorySubCategory]


class VoltalisConsumptionBreakdownDto(CustomModel):
    """Docstring pour VoltalisConsumptionBreakdownDto"""

    categories: list[VoltalisConsumptionDtoBreakdownCategory]


class VoltalisConsumptionDto(CustomModel):
    """Docstring pour VoltalisConsumption"""

    breakdown: VoltalisConsumptionBreakdownDto
    per_appliance: dict[int, list[VoltalisConsumptionDtoDevice]] = Field(alias="perAppliance")
