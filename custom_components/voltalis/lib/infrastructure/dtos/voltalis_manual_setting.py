from pydantic import Field

from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.models.manual_setting import VoltalisManualSetting
from custom_components.voltalis.lib.infrastructure.dtos.voltalis_device import VoltalisDeviceDtoModeEnum


class VoltalisManualSettingUpdateDto(CustomModel):
    """Class to represent manual setting update request DTO"""

    id_appliance: int = Field(alias="idAppliance")
    enabled: bool
    until_further_notice: bool = Field(alias="untilFurtherNotice")
    is_on: bool = Field(alias="isOn")
    mode: VoltalisDeviceDtoModeEnum
    end_date: str | None = Field(None, alias="endDate")
    temperature_target: float = Field(alias="temperatureTarget")


class VoltalisManualSettingDto(VoltalisManualSettingUpdateDto):
    """Class to represent manual setting of a Voltalis device DTO"""

    id: int

    def to_voltalis_manual_setting(self) -> VoltalisManualSetting:
        """Convert to domain model"""

        return VoltalisManualSetting(
            id=self.id,
            enabled=self.enabled,
            id_appliance=self.id_appliance,
            until_further_notice=self.until_further_notice,
            is_on=self.is_on,
            mode=self.mode.value.lower(),
            end_date=self.end_date,
            temperature_target=self.temperature_target,
        )
