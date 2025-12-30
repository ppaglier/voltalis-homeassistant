from enum import StrEnum

from pydantic import Field

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisDeviceDtoTypeEnum(StrEnum):
    """Enum for the type field"""

    HEATER = "HEATER"
    WATER_HEATER = "WATER_HEATER"
    OTHER = "OTHER"


class VoltalisDeviceDtoModulatorTypeEnum(StrEnum):
    """Enum for the modulator_type field"""

    VX_WIRE = "VX_WIRE"
    VX_RELAY = "VX_RELAY"


class VoltalisDeviceDtoProgTypeEnum(StrEnum):
    """Enum for the type field"""

    MANUAL = "MANUAL"
    DEFAULT = "DEFAULT"
    USER = "USER"
    QUICK = "QUICK"


class VoltalisDeviceDtoModeEnum(StrEnum):
    """Enum for the available_modes field"""

    ECO = "ECO"
    CONFORT = "CONFORT"
    TEMPERATURE = "TEMPERATURE"
    HORS_GEL = "HORS_GEL"
    NORMAL = "NORMAL"
    ECOV = "ECOV"
    OFF = "OFF"
    AUTO = "AUTO"


class VoltalisDeviceDtoProgramming(CustomModel):
    """Class to represent the status of a Voltalis device"""

    prog_type: VoltalisDeviceDtoProgTypeEnum = Field(alias="progType")
    id_manual_setting: int | None = Field(None, alias="idManualSetting")
    is_on: bool | None = Field(None, alias="isOn")
    mode: VoltalisDeviceDtoModeEnum | None = None
    temperature_target: float | None = None
    default_temperature: float | None = Field(None, alias="defaultTemperature")


class VoltalisDeviceDto(CustomModel):
    """Class to represent Voltalis devices"""

    id: int
    name: str
    type: VoltalisDeviceDtoTypeEnum
    modulator_type: VoltalisDeviceDtoModulatorTypeEnum = Field(alias="modulatorType")
    available_modes: list[VoltalisDeviceDtoModeEnum] = Field(alias="availableModes")
    programming: VoltalisDeviceDtoProgramming
