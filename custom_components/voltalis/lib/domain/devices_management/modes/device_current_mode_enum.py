from enum import StrEnum


class DeviceCurrentModeEnum(StrEnum):
    """Voltalis device preset select options."""

    COMFORT = "comfort"
    ECO = "eco"
    FROST_PROTECTION = "frost_protection"
    TEMPERATURE = "temperature"
    ON = "on"
    OFF = "off"
