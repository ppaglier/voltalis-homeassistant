from typing import Self

from custom_components.voltalis.lib.domain.devices_management.health.device_health import (
    DeviceHealth,
    DeviceHealthStatusEnum,
)
from custom_components.voltalis.lib.domain.shared.generic_builder import GenericBuilder


class DeviceHealthBuilder(GenericBuilder[DeviceHealth]):
    """Builder for DeviceHealth model."""

    DEFAULT_VALUES = DeviceHealth(
        status=DeviceHealthStatusEnum.OK,
    )

    def build(self) -> DeviceHealth:
        return DeviceHealth(**self.props)

    def with_status(self, status: DeviceHealthStatusEnum) -> Self:
        """Set the status of the device health."""
        return self._set_value("status", status)
