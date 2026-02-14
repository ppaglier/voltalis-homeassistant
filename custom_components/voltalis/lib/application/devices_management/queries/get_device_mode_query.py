from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class GetDeviceModeQuery(CustomModel):
    """Query to get the current mode of devices."""

    is_on: bool
    mode: DeviceModeEnum
