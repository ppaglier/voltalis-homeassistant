from enum import StrEnum

from pydantic import Field

from custom_components.voltalis.lib.domain.devices_management.devices.device import (
    Device,
    DeviceProgramming,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import (
    DeviceModeEnum,
    DeviceModulatorTypeEnum,
    DeviceTypeEnum,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class VoltalisDeviceDtoApplianceTypeEnum(StrEnum):
    """Enum for the type field"""

    HEATER = "HEATER"
    WATER_HEATER = "WATER_HEATER"
    OTHER = "OTHER"


VOLTALIS_DEVICE_TYPE_MAPPING = {
    VoltalisDeviceDtoApplianceTypeEnum.HEATER: DeviceTypeEnum.HEATER,
    VoltalisDeviceDtoApplianceTypeEnum.WATER_HEATER: DeviceTypeEnum.WATER_HEATER,
    VoltalisDeviceDtoApplianceTypeEnum.OTHER: DeviceTypeEnum.OTHER,
}


class VoltalisDeviceDtoModulatorTypeEnum(StrEnum):
    """Enum for the modulator_type field"""

    VX_WIRE = "VX_WIRE"
    VX_RELAY = "VX_RELAY"


VOLTALIS_DEVICE_MODULATOR_TYPE_MAPPING = {
    VoltalisDeviceDtoModulatorTypeEnum.VX_WIRE: DeviceModulatorTypeEnum.VX_WIRE,
    VoltalisDeviceDtoModulatorTypeEnum.VX_RELAY: DeviceModulatorTypeEnum.VX_RELAY,
}


class VoltalisDeviceDtoProgTypeEnum(StrEnum):
    """Enum for the type field"""

    MANUAL = "MANUAL"
    DEFAULT = "DEFAULT"
    USER = "USER"
    QUICK = "QUICK"


VOLTALIS_DEVICE_PROG_TYPE_MAPPING = {
    VoltalisDeviceDtoProgTypeEnum.MANUAL: ProgramTypeEnum.MANUAL,
    VoltalisDeviceDtoProgTypeEnum.DEFAULT: ProgramTypeEnum.DEFAULT,
    VoltalisDeviceDtoProgTypeEnum.USER: ProgramTypeEnum.USER,
}


class VoltalisDeviceDtoModeEnum(StrEnum):
    """Enum for the available_modes field"""

    ECO = "ECO"
    CONFORT = "CONFORT"
    TEMPERATURE = "TEMPERATURE"
    HORS_GEL = "HORS_GEL"
    NORMAL = "NORMAL"
    ECOV = "ECOV"
    OFF = "OFF"


VOLTALIS_DEVICE_MODE_MAPPING = {
    VoltalisDeviceDtoModeEnum.ECO: DeviceModeEnum.ECO,
    VoltalisDeviceDtoModeEnum.CONFORT: DeviceModeEnum.COMFORT,
    VoltalisDeviceDtoModeEnum.TEMPERATURE: DeviceModeEnum.TEMPERATURE,
    VoltalisDeviceDtoModeEnum.HORS_GEL: DeviceModeEnum.AWAY,
    VoltalisDeviceDtoModeEnum.NORMAL: DeviceModeEnum.ON,
    VoltalisDeviceDtoModeEnum.OFF: DeviceModeEnum.OFF,
}
REVERSED_MODE_MAPPING = {v: k for k, v in VOLTALIS_DEVICE_MODE_MAPPING.items()}


class VoltalisDeviceDtoProgramming(CustomModel):
    """Class to represent the status of a Voltalis device"""

    prog_type: VoltalisDeviceDtoProgTypeEnum = Field(alias="progType")
    id_manual_setting: int | None = Field(None, alias="idManualSetting")
    is_on: bool | None = Field(None, alias="isOn")
    mode: VoltalisDeviceDtoModeEnum | None = None
    temperature_target: float | None = Field(None, alias="temperatureTarget")
    default_temperature: float | None = Field(None, alias="defaultTemperature")


class VoltalisDeviceDto(CustomModel):
    """Class to represent Voltalis devices"""

    id: int
    name: str
    appliance_type: VoltalisDeviceDtoApplianceTypeEnum = Field(alias="applianceType")
    modulator_type: VoltalisDeviceDtoModulatorTypeEnum = Field(alias="modulatorType")
    available_modes: list[VoltalisDeviceDtoModeEnum] = Field(alias="availableModes")
    programming: VoltalisDeviceDtoProgramming

    @staticmethod
    def from_device(device: Device) -> "VoltalisDeviceDto":
        """Convert from domain model to DTO"""

        REVERSED_DEVICE_TYPE_MAPPING = {v: k for k, v in VOLTALIS_DEVICE_TYPE_MAPPING.items()}
        REVERSED_MODULATOR_TYPE_MAPPING = {v: k for k, v in VOLTALIS_DEVICE_MODULATOR_TYPE_MAPPING.items()}
        REVERSED_PROG_TYPE_MAPPING = {v: k for k, v in VOLTALIS_DEVICE_PROG_TYPE_MAPPING.items()}

        actual_mode: VoltalisDeviceDtoModeEnum | None = None
        if device.programming.mode:
            actual_mode = REVERSED_MODE_MAPPING.get(device.programming.mode, None)
            if device.programming.mode is DeviceModeEnum.ECO and device.has_ecov:
                actual_mode = VoltalisDeviceDtoModeEnum.ECOV

        return VoltalisDeviceDto(
            id=device.id,
            name=device.name,
            appliance_type=REVERSED_DEVICE_TYPE_MAPPING[device.type],
            modulator_type=REVERSED_MODULATOR_TYPE_MAPPING[device.modulator_type],
            available_modes=[REVERSED_MODE_MAPPING[mode] for mode in device.available_modes],
            programming=VoltalisDeviceDtoProgramming(
                prog_type=REVERSED_PROG_TYPE_MAPPING[device.programming.prog_type],
                id_manual_setting=device.programming.id_manual_setting,
                is_on=device.programming.is_on,
                mode=actual_mode,
                temperature_target=device.programming.temperature_target,
                default_temperature=device.programming.default_temperature,
            ),
        )

    def to_device(self) -> Device:
        """Convert to domain model"""

        actual_mode: DeviceModeEnum | None = None
        if self.programming.mode:
            actual_mode = VOLTALIS_DEVICE_MODE_MAPPING.get(self.programming.mode, None)
            if self.programming.mode is VoltalisDeviceDtoModeEnum.ECOV:
                actual_mode = DeviceModeEnum.ECO

        return Device(
            id=self.id,
            name=self.name,
            type=VOLTALIS_DEVICE_TYPE_MAPPING[self.appliance_type],
            modulator_type=VOLTALIS_DEVICE_MODULATOR_TYPE_MAPPING[self.modulator_type],
            available_modes=[
                VOLTALIS_DEVICE_MODE_MAPPING[mode]
                for mode in self.available_modes
                if mode in VOLTALIS_DEVICE_MODE_MAPPING
            ],
            has_ecov=VoltalisDeviceDtoModeEnum.ECOV in self.available_modes,
            programming=DeviceProgramming(
                prog_type=VOLTALIS_DEVICE_PROG_TYPE_MAPPING[self.programming.prog_type],
                id_manual_setting=self.programming.id_manual_setting,
                is_on=self.programming.is_on,
                mode=actual_mode,
                temperature_target=self.programming.temperature_target,
                default_temperature=self.programming.default_temperature,
            ),
        )
