from enum import StrEnum

from homeassistant.components.climate import PRESET_AWAY, PRESET_COMFORT, PRESET_ECO, PRESET_NONE


class DeviceCurrentPresetEnum(StrEnum):
    """Enum for device presets"""

    COMFORT = PRESET_COMFORT
    ECO = PRESET_ECO
    AWAY = PRESET_AWAY
    TEMPERATURE = "temperature"

    ON = "on"
    OFF = PRESET_NONE
    AUTO = "auto"
