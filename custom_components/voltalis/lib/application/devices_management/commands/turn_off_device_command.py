from custom_components.voltalis.lib.domain.devices_management.device.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class TurnOffDeviceCommand(CustomModel):
    """Command to turn off a climate device for a specified duration.

    Attributes:
        manual_setting_id: The ID of the manual setting to update
        device_id: The ID of the device (appliance)
        temperature: The target temperature to set when turning off (default: 16.0°C)
        duration_hours: Duration in hours to keep the device turned off (None = indefinite)
    """

    manual_setting_id: int
    device_id: int
    fallback_mode: DeviceModeEnum = DeviceModeEnum.ECO
    fallback_temperature: float = 16.0
    duration_hours: int | None = None
