from typing import Self

from custom_components.voltalis.lib.domain.devices_management.consumptions.device_consumption import (
    ConsumptionRecord,
    DeviceConsumption,
)
from custom_components.voltalis.lib.domain.shared.generic_builder import GenericBuilder


class DeviceConsumptionBuilder(GenericBuilder[DeviceConsumption]):
    """Builder for DeviceConsumption model."""

    DEFAULT_VALUES = DeviceConsumption(
        daily_consumption_records=[],
    )

    def build(self) -> DeviceConsumption:
        return DeviceConsumption(**self.props)

    def with_daily_consumption_records(self, consumptions: list[ConsumptionRecord]) -> Self:
        """Set the consumption records of the device."""
        return self._set_value("daily_consumption_records", consumptions)
