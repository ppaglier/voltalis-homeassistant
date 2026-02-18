from enum import StrEnum

from pydantic import Field

from custom_components.voltalis.lib.domain.devices_management.health.device_health import DeviceHealth
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


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

    @staticmethod
    def from_device_health(
        cs_appliance_id: int,
        device_health: DeviceHealth,
    ) -> "VoltalisDeviceHealthDto":
        """Convert from domain model"""

        return VoltalisDeviceHealthDto(
            cs_appliance_id=cs_appliance_id,
            status=device_health.status.value.upper(),
        )

    def to_device_health(self) -> DeviceHealth:
        """Convert to domain model"""

        return DeviceHealth(
            status=self.status.value.lower(),
        )
