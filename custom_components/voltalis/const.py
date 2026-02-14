"""Constants for the Voltalis integration."""

from homeassistant.const import UnitOfTemperature
from homeassistant.helpers import config_validation as cv

DOMAIN = "voltalis"
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

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
