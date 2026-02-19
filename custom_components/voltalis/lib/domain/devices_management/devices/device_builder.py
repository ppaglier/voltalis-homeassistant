from typing import Self

from custom_components.voltalis.lib.domain.devices_management.devices.device import Device, DeviceProgramming
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import (
    DeviceModeEnum,
    DeviceModulatorTypeEnum,
    DeviceTypeEnum,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum
from custom_components.voltalis.lib.domain.shared.generic_builder import GenericBuilder


class DeviceBuilder(GenericBuilder[Device]):
    """Builder for Device model."""

    DEFAULT_VALUES = Device(
        id=0,
        name="Device name",
        type=DeviceTypeEnum.HEATER,
        modulator_type=DeviceModulatorTypeEnum.VX_WIRE,
        available_modes=[DeviceModeEnum.COMFORT, DeviceModeEnum.ECO],
        has_ecov=False,
        programming=DeviceProgramming(
            prog_type=ProgramTypeEnum.DEFAULT,
            mode=DeviceModeEnum.ECO,
            temperature_target=0.0,
            default_temperature=0.0,
        ),
    )

    def build(self) -> Device:
        return Device(**self.props)

    def with_id(self, id: int) -> Self:
        """Set the id of the device."""
        return self._set_value("id", id)

    def with_name(self, name: str) -> Self:
        """Set the name of the device."""
        return self._set_value("name", name)

    def with_type(self, type: DeviceTypeEnum) -> Self:
        """Set the type of the device."""
        return self._set_value("type", type)

    def with_modulator_type(self, modulator_type: DeviceModulatorTypeEnum) -> Self:
        """Set the modulator type of the device."""
        return self._set_value("modulator_type", modulator_type)

    def with_available_modes(self, available_modes: list[DeviceModeEnum]) -> Self:
        """Set the available modes of the device."""
        return self._set_value("available_modes", available_modes)

    def with_has_ecov(self, has_ecov: bool) -> Self:
        """Set whether the device has ECOV mode."""
        return self._set_value("has_ecov", has_ecov)

    def with_programming(self, programming: DeviceProgramming) -> Self:
        """Set the programming of the device."""
        return self._set_value("programming", programming)

    def with_programming_mode(self, mode: DeviceModeEnum) -> Self:
        """Set the mode in the programming of the device."""

        programming = self._get_value("programming")
        programming["mode"] = mode
        return self._set_value("programming", programming)
