"""Constants for the Voltalis integration."""

from homeassistant.components.climate import PRESET_AWAY, PRESET_COMFORT, PRESET_ECO, PRESET_HOME, PRESET_NONE

DEFAULT_NAME = "Voltalis"
DOMAIN = "voltalis"

# Temps

DEFAULT_MIN_TEMP = 7
DEFAULT_MAX_TEMP = 24


# Presets

VOLTALIS_PRESET_MODES = {
    PRESET_ECO: "ECO",
    PRESET_COMFORT: "CONFORT",
    PRESET_HOME: "TEMPERATURE",
    PRESET_AWAY: "HORS_GEL",
    PRESET_NONE: "NORMAL",
}

HA_PRESET_MODES = {v: k for k, v in VOLTALIS_PRESET_MODES.items()}
