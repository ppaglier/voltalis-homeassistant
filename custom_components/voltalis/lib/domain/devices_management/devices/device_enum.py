from enum import StrEnum

from homeassistant.components.climate import PRESET_AWAY, PRESET_COMFORT, PRESET_ECO, PRESET_NONE


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

    COMFORT = PRESET_COMFORT
    ECO = PRESET_ECO
    AWAY = PRESET_AWAY
    TEMPERATURE = "temperature"

    ON = "on"
    OFF = PRESET_NONE
