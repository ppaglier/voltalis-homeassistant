from enum import StrEnum

from pydantic import Field

from custom_components.voltalis.lib.domain.devices_management.health.device_health import (
    DeviceHealth,
    DeviceHealthStatusEnum,
)
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


VOLTALIS_DEVICE_HEALTH_STATUS_MAPPING = {
    VoltalisDeviceHealthDtoStatusEnum.OK: DeviceHealthStatusEnum.OK,
    VoltalisDeviceHealthDtoStatusEnum.NOT_OK: DeviceHealthStatusEnum.NOT_OK,
    VoltalisDeviceHealthDtoStatusEnum.TEST_IN_PROGRESS: DeviceHealthStatusEnum.TEST_IN_PROGRESS,
    VoltalisDeviceHealthDtoStatusEnum.NO_CONSUMPTION: DeviceHealthStatusEnum.NO_CONSUMPTION,
    VoltalisDeviceHealthDtoStatusEnum.COMM_ERROR: DeviceHealthStatusEnum.COMM_ERROR,
    VoltalisDeviceHealthDtoStatusEnum.NO_CONSUMPTION_NO_CAPS: DeviceHealthStatusEnum.NO_CONSUMPTION,
    VoltalisDeviceHealthDtoStatusEnum.COMM_ERROR_NO_CAPS: DeviceHealthStatusEnum.COMM_ERROR,
}


class VoltalisDeviceHealthDto(CustomModel):
    """Class to represent a Voltalis device health DTO"""

    cs_appliance_id: int = Field(alias="csApplianceId")
    status: VoltalisDeviceHealthDtoStatusEnum

    @staticmethod
    def from_device_health(device_health: DeviceHealth) -> "VoltalisDeviceHealthDto":
        """Convert from domain model"""

        reversed_mapping = {v: k for k, v in VOLTALIS_DEVICE_HEALTH_STATUS_MAPPING.items()}

        return VoltalisDeviceHealthDto(
            cs_appliance_id=device_health.device_id,
            status=reversed_mapping[device_health.status],
        )

    def to_device_health(self) -> DeviceHealth:
        """Convert to domain model"""

        return DeviceHealth(
            device_id=self.cs_appliance_id,
            status=VOLTALIS_DEVICE_HEALTH_STATUS_MAPPING[self.status],
        )
