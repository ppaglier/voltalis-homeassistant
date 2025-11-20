from enum import StrEnum

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisHealthStatusEnum(StrEnum):
    """Enum for the type field"""

    OK = "ok"
    NOT_OK = "nok"
    TEST_IN_PROGRESS = "test_in_progress"
    NO_CONSUMPTION = "no_consumption"
    COMM_ERROR = "comm_error"


class VoltalisDeviceHealth(CustomModel):
    """Class to represent Voltalis devices"""

    status: VoltalisHealthStatusEnum
