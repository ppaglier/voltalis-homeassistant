from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class GetClimateCurrentActionQuery(CustomModel):
    """Query to get the current action of a climate device."""

    is_on: bool
    mode: DeviceModeEnum
