from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.models.device import VoltalisDeviceModeEnum, VoltalisDeviceTypeEnum


class VoltalisManualSetting(CustomModel):
    """Class to represent manual setting of a Voltalis device"""

    id: int
    enabled: bool
    id_appliance: int
    appliance_name: str
    appliance_type: VoltalisDeviceTypeEnum
    until_further_notice: bool
    is_on: bool
    mode: VoltalisDeviceModeEnum
    end_date: str | None = None
    temperature_target: float


class VoltalisManualSettingUpdate(CustomModel):
    """Class to represent manual setting update request"""

    enabled: bool
    id_appliance: int
    until_further_notice: bool
    is_on: bool
    mode: VoltalisDeviceModeEnum
    end_date: str | None = None
    temperature_target: float
