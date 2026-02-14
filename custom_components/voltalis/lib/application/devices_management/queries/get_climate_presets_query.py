from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class GetClimatePresetsQuery(CustomModel):
    """Query to get the possible presets of a device."""

    available_modes: list[DeviceModeEnum]
