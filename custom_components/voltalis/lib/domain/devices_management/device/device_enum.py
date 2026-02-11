from enum import StrEnum


class DeviceTypeEnum(StrEnum):
    """Enum for the type field"""

    HEATER = "heater"
    WATER_HEATER = "water_heater"
    OTHER = "other"


class DeviceModulatorTypeEnum(StrEnum):
    """Enum for the modulator_type field"""

    VX_WIRE = "vx_wire"
    VX_RELAY = "vx_relay"


class DeviceModeEnum(StrEnum):
    """Enum for the available_modes field"""

    ECO = "eco"
    CONFORT = "confort"
    TEMPERATURE = "temperature"
    HORS_GEL = "hors_gel"
    NORMAL = "normal"
    ECOV = "ecov"
    OFF = "off"
    AUTO = "auto"
