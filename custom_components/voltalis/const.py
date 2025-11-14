"""Constants for the Voltalis integration."""

from homeassistant.components.climate import PRESET_AWAY, PRESET_COMFORT, PRESET_ECO, PRESET_HOME, PRESET_NONE
from homeassistant.helpers import config_validation as cv

from custom_components.voltalis.lib.domain.device import VoltalisDeviceModeEnum

DOMAIN = "voltalis"
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

# Temps

DEFAULT_MIN_TEMP = 7
DEFAULT_MAX_TEMP = 24

TEMP_UNITS = {
    "CELSIUS": "°C",
    "FAHRENHEIT": "°F",
}


# Presets
VOLTALIS_TO_HA_MODES = {
    VoltalisDeviceModeEnum.ECO: PRESET_ECO,
    VoltalisDeviceModeEnum.ECOV: PRESET_ECO,
    VoltalisDeviceModeEnum.CONFORT: PRESET_COMFORT,
    VoltalisDeviceModeEnum.TEMPERATURE: PRESET_HOME,
    VoltalisDeviceModeEnum.HORS_GEL: PRESET_AWAY,
    VoltalisDeviceModeEnum.NORMAL: PRESET_NONE,
}

HA_TO_VOLTALIS_MODES = {
    PRESET_ECO: VoltalisDeviceModeEnum.ECO,
    PRESET_COMFORT: VoltalisDeviceModeEnum.CONFORT,
    PRESET_HOME: VoltalisDeviceModeEnum.TEMPERATURE,
    PRESET_AWAY: VoltalisDeviceModeEnum.HORS_GEL,
    PRESET_NONE: VoltalisDeviceModeEnum.NORMAL,
}
