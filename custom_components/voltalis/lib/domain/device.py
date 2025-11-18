from enum import StrEnum

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisDeviceTypeEnum(StrEnum):
    """Enum for the type field"""

    HEATER = "HEATER"
    WATER_HEATER = "WATER_HEATER"


class VoltalisDeviceModulatorTypeEnum(StrEnum):
    """Enum for the modulator_type field"""

    VX_WIRE = "VX_WIRE"
    VX_RELAY = "VX_RELAY"


class VoltalisDeviceModeEnum(StrEnum):
    """Enum for the available_modes field"""

    ECO = "ECO"
    CONFORT = "CONFORT"
    TEMPERATURE = "TEMPERATURE"
    HORS_GEL = "HORS_GEL"
    NORMAL = "NORMAL"
    ECOV = "ECOV"


class VoltalisDeviceProgTypeEnum(StrEnum):
    """Enum for the type field"""

    MANUAL = "MANUAL"
    DEFAULT = "DEFAULT"
    USER = "USER"

class VoltalisDeviceProgrammingStatus:
    """Class to represent the status of a Voltalis device"""

    prog_type: VoltalisDeviceProgTypeEnum
    prog_name: str
    id_manual_setting: int | None = None
    is_on: bool = None
    until_further_notice: bool | None = None
    mode: VoltalisDeviceModeEnum | None = None
    id_planning: int = None
    end_date: str | None = None
    temperature_target: float | None = None
    default_temperature: float | None = None

class VoltalisDevice(CustomModel):
    """Class to represent Voltalis devices"""

    id: int
    name: str
    type: VoltalisDeviceTypeEnum
    modulator_type: VoltalisDeviceModulatorTypeEnum
    available_modes: list[VoltalisDeviceModeEnum]
    programming: VoltalisDeviceProgrammingStatus
    heating_level: int | None = None
