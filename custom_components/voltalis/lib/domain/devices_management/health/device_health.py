from enum import StrEnum

from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class DeviceHealthStatusEnum(StrEnum):
    """Enum for the type field"""

    OK = "ok"
    NOT_OK = "nok"
    TEST_IN_PROGRESS = "test_in_progress"
    NO_CONSUMPTION = "no_consumption"
    COMM_ERROR = "comm_error"


class DeviceHealth(CustomModel):
    """Class to represent Voltalis devices health"""

    status: DeviceHealthStatusEnum
