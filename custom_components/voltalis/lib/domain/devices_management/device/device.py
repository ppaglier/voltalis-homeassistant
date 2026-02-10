from custom_components.voltalis.lib.domain.devices_management.device.device_enum import (
    VoltalisDeviceModeEnum,
    VoltalisDeviceModulatorTypeEnum,
    VoltalisDeviceTypeEnum,
)
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel
from custom_components.voltalis.lib.domain.voltalis_programs.voltalis_program_enum import VoltalisDeviceProgTypeEnum


class VoltalisDeviceProgramming(CustomModel):
    """Class to represent the status of a Voltalis device"""

    prog_type: VoltalisDeviceProgTypeEnum
    id_manual_setting: int | None = None
    is_on: bool | None = None
    mode: VoltalisDeviceModeEnum | None = None
    temperature_target: float | None = None
    default_temperature: float | None = None


class VoltalisDevice(CustomModel):
    """Class to represent Voltalis devices"""

    id: int
    name: str
    type: VoltalisDeviceTypeEnum
    modulator_type: VoltalisDeviceModulatorTypeEnum
    available_modes: list[VoltalisDeviceModeEnum]
    programming: VoltalisDeviceProgramming
