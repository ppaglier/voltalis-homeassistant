from typing import Self

from custom_components.voltalis.lib.domain.devices_management.consumptions.device_consumption import DeviceConsumption
from custom_components.voltalis.lib.domain.shared.generic_builder import GenericBuilder


class DeviceConsumptionBuilder(GenericBuilder[DeviceConsumption]):
    """Builder for DeviceConsumption model."""

    DEFAULT_VALUES = DeviceConsumption(
        daily_consumption=0.0,
    )

    props: dict = {}

    def __init__(self, props: dict = {}):
        self.props = {**DeviceConsumptionBuilder.DEFAULT_VALUES.model_dump(), **props}

    def build(self) -> DeviceConsumption:
        return DeviceConsumption(**self.props)

    def with_daily_consumption(self, daily_consumption: float) -> Self:
        """Set the daily consumption of the device."""
        return self._set_value("daily_consumption", daily_consumption)
