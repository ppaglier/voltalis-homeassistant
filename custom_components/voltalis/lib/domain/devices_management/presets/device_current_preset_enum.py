from enum import StrEnum


class DeviceCurrentPresetEnum(StrEnum):
    """Preset modes for climate devices."""

    COMFORT = "comfort"
    ECO = "eco"
    FROST_PROTECTION = "frost_protection"
    TEMPERATURE = "temperature"

    AUTO = "auto"
    ON = "on"
    OFF = "off"
