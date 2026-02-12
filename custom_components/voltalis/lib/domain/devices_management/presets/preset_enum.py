from enum import StrEnum


class DevicePresetEnum(StrEnum):
    """Preset modes for climate devices."""

    COMFORT = "comfort"
    ECO = "eco"
    FROST_PROTECTION = "frost_protection"
    TEMPERATURE = "temperature"

    ON = "on"
    OFF = "off"
    AUTO = "auto"
