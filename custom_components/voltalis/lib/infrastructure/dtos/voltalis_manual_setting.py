from enum import StrEnum

from pydantic import Field

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisManualSettingDtoModeEnum(StrEnum):
    """Enum for the available_modes field"""

    ECO = "ECO"
    CONFORT = "CONFORT"
    TEMPERATURE = "TEMPERATURE"
    HORS_GEL = "HORS_GEL"
    NORMAL = "NORMAL"
    ECOV = "ECOV"
    OFF = "OFF"
    AUTO = "AUTO"


class VoltalisManualSettingDto(CustomModel):
    """Class to represent manual setting of a Voltalis device DTO"""

    id: int
    id_appliance: int = Field(alias="idAppliance")
    enabled: bool
    until_further_notice: bool = Field(alias="untilFurtherNotice")
    is_on: bool = Field(alias="isOn")
    mode: VoltalisManualSettingDtoModeEnum
    end_date: str | None = Field(None, alias="endDate")
    temperature_target: float = Field(alias="temperatureTarget")
