"""Constants for the Voltalis integration."""

from enum import StrEnum

from homeassistant.components.climate import PRESET_AWAY, PRESET_COMFORT, PRESET_ECO, PRESET_HOME, PRESET_NONE
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers import config_validation as cv

from custom_components.voltalis.lib.domain.device import VoltalisDeviceModeEnum

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


class HomeAssistantPresetModes(StrEnum):
    """Home Assistant presets that will be used for Voltalis devices."""

    ECO = PRESET_ECO
    COMFORT = PRESET_COMFORT
    HOME = PRESET_HOME
    AWAY = PRESET_AWAY
    NONE = PRESET_NONE


# Presets
VOLTALIS_TO_HA_MODES = {
    VoltalisDeviceModeEnum.ECO: HomeAssistantPresetModes.ECO,
    VoltalisDeviceModeEnum.ECOV: HomeAssistantPresetModes.ECO,
    VoltalisDeviceModeEnum.CONFORT: HomeAssistantPresetModes.COMFORT,
    VoltalisDeviceModeEnum.TEMPERATURE: HomeAssistantPresetModes.NONE,
    VoltalisDeviceModeEnum.HORS_GEL: HomeAssistantPresetModes.AWAY,
    VoltalisDeviceModeEnum.NORMAL: HomeAssistantPresetModes.NONE,
}

HA_TO_VOLTALIS_MODES = {
    HomeAssistantPresetModes.ECO: VoltalisDeviceModeEnum.ECO,
    HomeAssistantPresetModes.COMFORT: VoltalisDeviceModeEnum.CONFORT,
    HomeAssistantPresetModes.NONE: VoltalisDeviceModeEnum.TEMPERATURE,
    HomeAssistantPresetModes.AWAY: VoltalisDeviceModeEnum.HORS_GEL,
    HomeAssistantPresetModes.NONE: VoltalisDeviceModeEnum.NORMAL,
}
