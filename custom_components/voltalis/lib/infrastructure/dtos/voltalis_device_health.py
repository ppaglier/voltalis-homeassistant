from enum import StrEnum

from pydantic import Field

from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.models.device_health import VoltalisDeviceHealth


class VoltalisDeviceHealthDtoStatusEnum(StrEnum):
    """Enum for the type field"""

    OK = "OK"
    NOT_OK = "NOK"
    TEST_IN_PROGRESS = "TEST_IN_PROGRESS"
    NO_CONSUMPTION = "NO_CONSUMPTION"
    COMM_ERROR = "COMM_ERROR"

    NO_CONSUMPTION_NO_CAPS = "no_consumption"
    COMM_ERROR_NO_CAPS = "comm_error"


class VoltalisDeviceHealthDto(CustomModel):
    """Class to represent a Voltalis device health DTO"""

    cs_appliance_id: int = Field(alias="csApplianceId")
    status: VoltalisDeviceHealthDtoStatusEnum

    def to_voltalis_device_health(self) -> VoltalisDeviceHealth:
        """Convert to domain model"""

        return VoltalisDeviceHealth(
            status=self.status.value.lower(),
        )
