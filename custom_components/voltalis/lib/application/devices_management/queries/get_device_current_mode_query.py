from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class GetDeviceCurrentModeQuery(CustomModel):
    """Query to get the current mode of devices."""

    is_on: bool
    mode: DeviceModeEnum
