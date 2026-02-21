from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import (
    DeviceModeEnum,
    DeviceModulatorTypeEnum,
    DeviceTypeEnum,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import (
    ProgramTypeEnum,
)
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class DeviceProgramming(CustomModel):
    """Class to represent the status of a Voltalis device"""

    prog_type: ProgramTypeEnum

    is_on: bool = False
    mode: DeviceModeEnum

    temperature_target: float | None = None
    default_temperature: float | None = None


class Device(CustomModel):
    """Class to represent Voltalis devices"""

    id: int
    name: str

    type: DeviceTypeEnum
    modulator_type: DeviceModulatorTypeEnum

    available_modes: list[DeviceModeEnum]
    has_ecov: bool

    programming: DeviceProgramming
