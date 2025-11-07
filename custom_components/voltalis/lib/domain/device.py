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


class VoltalisDeviceConsumption(CustomModel):
    """Class to represent Voltalis devices consumption"""

    realtime: float
    daily: float


class VoltalisDevice(CustomModel):
    """Class to represent Voltalis devices"""

    id: int
    name: str
    status: bool | None = None
    type: VoltalisDeviceTypeEnum
    modulator_type: VoltalisDeviceModulatorTypeEnum
    available_modes: list[VoltalisDeviceModeEnum]
    prog_type: VoltalisDeviceProgTypeEnum

    # consumption: VoltalisDeviceConsumption
