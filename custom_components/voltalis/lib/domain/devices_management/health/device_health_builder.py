from typing import Self

from custom_components.voltalis.lib.domain.devices_management.devices.device_builder import DeviceBuilder
from custom_components.voltalis.lib.domain.devices_management.health.device_health import (
    DeviceHealth,
    DeviceHealthStatusEnum,
)
from custom_components.voltalis.lib.domain.shared.generic_builder import GenericBuilder


class DeviceHealthBuilder(GenericBuilder[DeviceHealth]):
    """Builder for DeviceHealth model."""

    DEFAULT_VALUES = DeviceHealth(
        device_id=DeviceBuilder.DEFAULT_VALUES.id,
        status=DeviceHealthStatusEnum.OK,
    )

    def build(self) -> DeviceHealth:
        return DeviceHealth(**self.props)

    def with_device_id(self, device_id: int) -> Self:
        """Set the device id of the device health."""
        return self._set_value("device_id", device_id)

    def with_status(self, status: DeviceHealthStatusEnum) -> Self:
        """Set the status of the device health."""
        return self._set_value("status", status)
