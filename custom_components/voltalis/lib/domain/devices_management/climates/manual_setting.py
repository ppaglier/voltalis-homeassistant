from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class ManualSetting(CustomModel):
    """Class to represent manual setting of a Voltalis device"""

    id: int
    enabled: bool
    id_appliance: int
    until_further_notice: bool
    is_on: bool
    mode: DeviceModeEnum
    end_date: str | None = None
    temperature_target: float


class ManualSettingUpdate(CustomModel):
    """Class to represent manual setting update request"""

    enabled: bool
    id_appliance: int
    until_further_notice: bool
    is_on: bool
    mode: DeviceModeEnum
    end_date: str | None = None
    temperature_target: float
