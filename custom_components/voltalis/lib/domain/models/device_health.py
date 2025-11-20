from enum import StrEnum

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisHealthStatusEnum(StrEnum):
    """Enum for the type field"""

    OK = "ok"
    NOT_OK = "nok"
    TEST_IN_PROGRESS = "other"


class VoltalisDeviceHealth(CustomModel):
    """Class to represent Voltalis devices"""

    status: VoltalisHealthStatusEnum
