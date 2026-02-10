from enum import StrEnum


class VoltalisDeviceProgTypeEnum(StrEnum):
    """Enum for the type field"""

    MANUAL = "manual"
    DEFAULT = "default"
    USER = "user"
    QUICK = "quick"
