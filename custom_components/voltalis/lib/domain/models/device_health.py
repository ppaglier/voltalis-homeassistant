from enum import StrEnum

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisHealthStatusEnum(StrEnum):
    """Enum for the type field"""

    OK = "OK"
    NOT_OK = "NOK"
    TEST_IN_PROGRESS = "OTHER"


class VoltalisDeviceHealth(CustomModel):
    """Class to represent Voltalis devices"""

    status: VoltalisHealthStatusEnum
