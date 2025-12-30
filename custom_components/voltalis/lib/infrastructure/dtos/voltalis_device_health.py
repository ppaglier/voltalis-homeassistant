from enum import StrEnum

from pydantic import Field

from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisDeviceHealthDtoStatusEnum(StrEnum):
    """Enum for the type field"""

    OK = "OK"
    NOT_OK = "NOK"
    TEST_IN_PROGRESS = "TEST_IN_PROGRESS"
    NO_CONSUMPTION = "no_consumption"
    COMM_ERROR = "comm_error"

    NO_CONSUMPTION_CAPS = "NO_CONSUMPTION"
    COMM_ERROR_CAPS = "COMM_ERROR"


class VoltalisDeviceHealthDto(CustomModel):
    """Class to represent a Voltalis device health DTO"""

    cs_appliance_id: int = Field(alias="csApplianceId")
    status: VoltalisDeviceHealthDtoStatusEnum
