"""Constants for the Voltalis integration."""

from enum import StrEnum

from homeassistant.const import UnitOfTemperature
from homeassistant.helpers import config_validation as cv

DOMAIN = "voltalis"
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


VOLTALIS_API_BASE_URL = "https://api.myvoltalis.com"
VOLTALIS_API_LOGIN_ROUTE = "/auth/login"

CLIMATE_UNIT = UnitOfTemperature.CELSIUS
CLIMATE_TEMP_STEP = 0.5
CLIMATE_BOOST_TEMP_INCREASE = 2.0
CLIMATE_BOOST_DURATION = 2.0  # in hours

CONF_LOG_LEVEL = "log_level"
CONF_CLIMATE_MIN_TEMP = "climate_min_temp"
CONF_CLIMATE_MAX_TEMP = "climate_max_temp"
CONF_DEFAULT_TEMP = "default_temp"
CONF_DEFAULT_AWAY_TEMP = "default_away_temp"
CONF_DEFAULT_ECO_TEMP = "default_eco_temp"
CONF_DEFAULT_COMFORT_TEMP = "default_comfort_temp"
CONF_DEFAULT_WATER_HEATER_TEMP = "default_water_heater_temp"


class LogLevelEnum(StrEnum):
    """Log levels for the Voltalis integration."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


DEFAULT_LOG_LEVEL = LogLevelEnum.INFO


# Temperature defaults for climate control
DEFAULT_CLIMATE_MIN_TEMP = 7.0
DEFAULT_CLIMATE_MAX_TEMP = 30.0
# Default temperatures for different presets and water heater
DEFAULT_TEMP = 18.0
DEFAULT_AWAY_TEMP = 7.0
DEFAULT_ECO_TEMP = 15.5
DEFAULT_COMFORT_TEMP = 21.0
DEFAULT_WATER_HEATER_TEMP = 55.0
