from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class DisableManualModeCommand(CustomModel):
    """Command to disable manual mode for a climate device.

    Attributes:
        device: The device for which to disable manual mode
        fallback_mode: The mode to set when disabling manual mode
        fallback_temperature: The target temperature to set when disabling manual mode
    """

    device: DeviceDto
    fallback_mode: DeviceModeEnum | None = None
    fallback_temperature: float | None = None
