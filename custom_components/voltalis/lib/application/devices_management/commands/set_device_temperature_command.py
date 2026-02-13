from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class SetDeviceTemperatureCommand(CustomModel):
    """Command to set target temperature for a climate device.

    Attributes:
        manual_setting_id: The ID of the manual setting to update
        device: The device for which to set the temperature
        temperature: The target temperature to set
        mode: The mode to use (default: TEMPERATURE)
        duration_hours: Duration in hours (None = indefinite)
    """

    manual_setting_id: int
    device: DeviceDto
    temperature: float | None = None
    mode: DeviceModeEnum = DeviceModeEnum.TEMPERATURE
    duration_hours: int | None = None
