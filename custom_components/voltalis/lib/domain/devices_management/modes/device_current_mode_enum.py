from enum import StrEnum

from homeassistant.components.climate import PRESET_AWAY, PRESET_COMFORT, PRESET_ECO, PRESET_NONE


class DeviceCurrentModeEnum(StrEnum):
    """Voltalis device preset select options."""

    COMFORT = PRESET_COMFORT
    ECO = PRESET_ECO
    AWAY = PRESET_AWAY
    TEMPERATURE = "temperature"

    ON = "on"
    OFF = PRESET_NONE
