"""Constants for the Voltalis integration."""

from homeassistant.components.climate import PRESET_AWAY, PRESET_COMFORT, PRESET_ECO, PRESET_HOME, PRESET_NONE
from homeassistant.helpers import config_validation as cv

from custom_components.voltalis.lib.domain.device import VoltalisDeviceModeEnum

DOMAIN = "voltalis"
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

VOLTALIS_API_BASE_URL = "https://api.myvoltalis.com"
VOLTALIS_API_LOGIN_ROUTE = "/auth/login"

# Temperature defaults for climate control
CLIMATE_MIN_TEMP = 7.0
CLIMATE_MAX_TEMP = 30.0
CLIMATE_TEMP_STEP = 0.5
CLIMATE_DEFAULT_TEMP = 18.0
CLIMATE_COMFORT_TEMP = 21.0
CLIMATE_BOOST_TEMP_INCREASE = 2.0

# Duration defaults (in hours)
DEFAULT_MANUAL_MODE_DURATION = 24
DEFAULT_BOOST_DURATION = 2.0
UNTIL_FURTHER_NOTICE_DURATION_DAYS = 365

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
