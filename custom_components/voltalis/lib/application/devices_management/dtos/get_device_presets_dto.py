from custom_components.voltalis.lib.domain.devices_management.presets.preset_enum import DeviceCurrentPresetEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class GetDevicePresetsDto(CustomModel):
    """DTO to get the possible presets of a device."""

    presets: list[DeviceCurrentPresetEnum]
    has_on_mode: bool
