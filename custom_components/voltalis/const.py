"""Constants for the Voltalis integration."""

from enum import StrEnum

from homeassistant.const import UnitOfTemperature
from homeassistant.helpers import config_validation as cv

DOMAIN = "voltalis"
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

CONF_CLIMATE_MIN_TEMP = "climate_min_temp"
CONF_CLIMATE_MAX_TEMP = "climate_max_temp"
CONF_CLIMATE_DEFAULT_TEMP = "climate_default_temp"
CONF_CLIMATE_COMFORT_TEMP = "climate_comfort_temp"
CONF_LOG_LEVEL = "log_level"


class LogLevelEnum(StrEnum):
    """Log levels for the Voltalis integration."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


LOG_LEVEL_DEFAULT = LogLevelEnum.INFO

VOLTALIS_API_BASE_URL = "https://api.myvoltalis.com"
VOLTALIS_API_LOGIN_ROUTE = "/auth/login"


# Temperature defaults for climate control
CLIMATE_UNIT = UnitOfTemperature.CELSIUS
CLIMATE_MIN_TEMP = 7.0
CLIMATE_MAX_TEMP = 30.0
CLIMATE_TEMP_STEP = 0.5
CLIMATE_DEFAULT_TEMP = 18.0
CLIMATE_COMFORT_TEMP = 21.0
CLIMATE_BOOST_TEMP_INCREASE = 2.0
CLIMATE_BOOST_DURATION = 2.0  # in hours
