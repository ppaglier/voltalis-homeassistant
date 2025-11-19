"""Constants for the Voltalis integration."""

from enum import StrEnum

from homeassistant.components.climate import PRESET_AWAY, PRESET_COMFORT, PRESET_ECO, PRESET_HOME, PRESET_NONE
from homeassistant.const import UnitOfTemperature
from homeassistant.helpers import config_validation as cv

from custom_components.voltalis.lib.domain.models.device import VoltalisDeviceModeEnum

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


class HomeAssistantPresetModeEnum(StrEnum):
    """Home Assistant presets that will be used for Voltalis devices."""

    ECO = PRESET_ECO
    COMFORT = PRESET_COMFORT
    HOME = PRESET_HOME
    AWAY = PRESET_AWAY
    NONE = PRESET_NONE


class VoltalisProgramSelectOptionsEnum(StrEnum):
    """Enum for Voltalis program select options."""

    COMFORT = "comfort"
    ECO = "eco"
    FROST_PROTECTION = "frost_protection"
    TEMPERATURE = "temperature"
    OFF = "off"
    AUTO = "auto"


# Presets (Ordered to match typical user expectations)
VOLTALIS_TO_HA_MODES = {
    VoltalisDeviceModeEnum.CONFORT: HomeAssistantPresetModeEnum.COMFORT,
    VoltalisDeviceModeEnum.ECO: HomeAssistantPresetModeEnum.ECO,
    VoltalisDeviceModeEnum.ECOV: HomeAssistantPresetModeEnum.ECO,
    VoltalisDeviceModeEnum.HORS_GEL: HomeAssistantPresetModeEnum.AWAY,
    VoltalisDeviceModeEnum.NORMAL: HomeAssistantPresetModeEnum.NONE,
    VoltalisDeviceModeEnum.TEMPERATURE: HomeAssistantPresetModeEnum.NONE,
}

HA_TO_VOLTALIS_MODES = {
    HomeAssistantPresetModeEnum.COMFORT: VoltalisDeviceModeEnum.CONFORT,
    HomeAssistantPresetModeEnum.ECO: VoltalisDeviceModeEnum.ECO,
    HomeAssistantPresetModeEnum.AWAY: VoltalisDeviceModeEnum.HORS_GEL,
    HomeAssistantPresetModeEnum.NONE: VoltalisDeviceModeEnum.NORMAL,
}

# Mappings between Voltalis device modes and program select options
VOLTALIS_MODES_TO_VOLTALIS_PROGRAM_SELECT_OPTIONS = {
    VoltalisDeviceModeEnum.CONFORT: VoltalisProgramSelectOptionsEnum.COMFORT,
    VoltalisDeviceModeEnum.ECO: VoltalisProgramSelectOptionsEnum.ECO,
    VoltalisDeviceModeEnum.ECOV: VoltalisProgramSelectOptionsEnum.ECO,
    VoltalisDeviceModeEnum.HORS_GEL: VoltalisProgramSelectOptionsEnum.FROST_PROTECTION,
    VoltalisDeviceModeEnum.TEMPERATURE: VoltalisProgramSelectOptionsEnum.TEMPERATURE,
}

VOLTALIS_PROGRAM_SELECT_OPTIONS_TO_VOLTALIS_MODES = {
    VoltalisProgramSelectOptionsEnum.COMFORT: VoltalisDeviceModeEnum.CONFORT,
    VoltalisProgramSelectOptionsEnum.ECO: VoltalisDeviceModeEnum.ECO,
    VoltalisProgramSelectOptionsEnum.FROST_PROTECTION: VoltalisDeviceModeEnum.HORS_GEL,
    VoltalisProgramSelectOptionsEnum.TEMPERATURE: VoltalisDeviceModeEnum.TEMPERATURE,
}
