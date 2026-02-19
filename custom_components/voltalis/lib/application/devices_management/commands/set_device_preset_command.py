from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.domain.devices_management.presets.preset_enum import DeviceCurrentPresetEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class SetDevicePresetCommand(CustomModel):
    """Command to set a preset mode for a climate device.

    Attributes:
        device_id: The ID of the device (appliance)
        preset: The preset to apply (auto, comfort, eco, frost_protection, off)
        temperature: The target temperature to use (only for TEMPERATURE preset)
        duration_hours: Duration in hours (None = indefinite)
    """

    device: DeviceDto
    preset: DeviceCurrentPresetEnum
    temperature: float | None = None
    duration_hours: int | None = None
    has_on_mode: bool = False
    climate_mode: bool = False
