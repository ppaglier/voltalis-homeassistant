from homeassistant.components.climate.const import HVACAction

from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class SetClimateActionCommand(CustomModel):
    """Command to set climate action for a device."""

    manual_setting_id: int
    device: DeviceDto
    action: HVACAction
