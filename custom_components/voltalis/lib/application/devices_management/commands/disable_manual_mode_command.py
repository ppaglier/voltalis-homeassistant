from custom_components.voltalis.lib.domain.devices_management.device.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class DisableManualModeCommand(CustomModel):
    """Command to disable manual mode for a climate device.

    Attributes:
        manual_setting_id: The ID of the manual setting to update
        device_id: The ID of the device (appliance)
        fallback_mode: The mode to set when disabling manual mode (default: ECO)
        fallback_temperature: The target temperature to set when disabling manual mode (default: 19.0°C)
    """

    manual_setting_id: int
    device_id: int
    fallback_mode: DeviceModeEnum = DeviceModeEnum.ECO
    fallback_temperature: float = 19.0
