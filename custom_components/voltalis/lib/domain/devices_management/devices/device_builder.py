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
        available_modes=[DeviceModeEnum.AUTO, DeviceModeEnum.CONFORT, DeviceModeEnum.ECO, DeviceModeEnum.OFF],
        programming=DeviceProgramming(
            prog_type=ProgramTypeEnum.DEFAULT,
            mode=DeviceModeEnum.OFF,
            temperature_target=0.0,
            default_temperature=0.0,
        ),
    )

    props: dict = {}

    def __init__(self, props: dict = {}):
        self.props = {**DeviceBuilder.DEFAULT_VALUES.model_dump(), **props}

    def build(self) -> Device:
        return Device(**self.props)

    def with_id(self, id: int) -> Self:
        """Set the id of the device."""
        return self._set_value("id", id)
