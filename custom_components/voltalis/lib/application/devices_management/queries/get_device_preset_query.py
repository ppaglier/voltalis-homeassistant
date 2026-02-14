from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class GetDevicePresetQuery(CustomModel):
    """Query to get the current preset of devices."""

    is_on: bool
    id_manual_setting: int | None = None
    mode: DeviceModeEnum | None = None
    climate_mode: bool = False
