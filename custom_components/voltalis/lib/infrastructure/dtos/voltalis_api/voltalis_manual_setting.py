from datetime import datetime

from pydantic import Field

from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import ManualSetting
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_api.voltalis_device import (
    VOLTALIS_DEVICE_MODE_MAPPING,
    VoltalisDeviceDtoModeEnum,
)


class VoltalisManualSettingUpdateDto(CustomModel):
    """Class to represent manual setting update request DTO"""

    id_appliance: int = Field(alias="idAppliance")
    enabled: bool
    until_further_notice: bool = Field(alias="untilFurtherNotice")
    is_on: bool = Field(alias="isOn")
    mode: VoltalisDeviceDtoModeEnum
    end_date: datetime | None = Field(None, alias="endDate")
    temperature_target: float = Field(alias="temperatureTarget")


class VoltalisManualSettingDto(VoltalisManualSettingUpdateDto):
    """Class to represent manual setting of a Voltalis device DTO"""

    id: int

    @staticmethod
    def from_manual_setting(
        manual_setting: ManualSetting,
    ) -> "VoltalisManualSettingDto":
        """Convert from domain model"""

        REVERSED_MODE_MAPPING = {v: k for k, v in VOLTALIS_DEVICE_MODE_MAPPING.items()}

        return VoltalisManualSettingDto(
            id=manual_setting.id,
            enabled=manual_setting.enabled,
            id_appliance=manual_setting.id_appliance,
            until_further_notice=manual_setting.until_further_notice,
            is_on=manual_setting.is_on,
            mode=REVERSED_MODE_MAPPING[manual_setting.mode],
            end_date=manual_setting.end_date,
            temperature_target=manual_setting.temperature_target,
        )

    def to_manual_setting(self) -> ManualSetting:
        """Convert to domain model"""

        return ManualSetting(
            id=self.id,
            enabled=self.enabled,
            id_appliance=self.id_appliance,
            until_further_notice=self.until_further_notice,
            is_on=self.is_on,
            mode=VOLTALIS_DEVICE_MODE_MAPPING[self.mode],
            end_date=self.end_date,
            temperature_target=self.temperature_target,
        )
