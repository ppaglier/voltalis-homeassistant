from datetime import datetime
from typing import Self

from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import ManualSetting
from custom_components.voltalis.lib.domain.devices_management.devices.device_builder import DeviceBuilder
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.generic_builder import GenericBuilder


class ManualSettingBuilder(GenericBuilder[ManualSetting]):
    """Builder for ManualSetting model."""

    DEFAULT_VALUES = ManualSetting(
        id=0,
        enabled=False,
        id_appliance=DeviceBuilder.DEFAULT_VALUES.id,
        until_further_notice=True,
        is_on=False,
        mode=DeviceModeEnum.OFF,
        end_date=None,
        temperature_target=0.0,
    )

    props: dict = {}

    def __init__(self, props: dict = {}):
        self.props = {**ManualSettingBuilder.DEFAULT_VALUES.model_dump(), **props}

    def build(self) -> ManualSetting:
        return ManualSetting(**self.props)

    def with_id(self, id: int) -> Self:
        """Set the id of the manualSetting."""
        return self._set_value("id", id)

    def with_enabled(self, enabled: bool) -> Self:
        """Set whether the manual setting is enabled."""
        return self._set_value("enabled", enabled)

    def with_id_appliance(self, id_appliance: int) -> Self:
        """Set the id of the appliance associated with the manual setting."""
        return self._set_value("id_appliance", id_appliance)

    def with_until_further_notice(self, until_further_notice: bool) -> Self:
        """Set whether the manual setting is until further notice."""
        return self._set_value("until_further_notice", until_further_notice)

    def with_is_on(self, is_on: bool) -> Self:
        """Set whether the device should be turned on."""
        return self._set_value("is_on", is_on)

    def with_mode(self, mode: DeviceModeEnum) -> Self:
        """Set the mode of the device."""
        return self._set_value("mode", mode)

    def with_end_date(self, end_date: datetime | None) -> Self:
        """Set the end date of the manual setting."""
        return self._set_value("end_date", end_date)

    def with_temperature_target(self, temperature_target: float) -> Self:
        """Set the target temperature of the manual setting."""
        return self._set_value("temperature_target", temperature_target)
