from custom_components.voltalis.lib.domain.devices_management.presets.device_current_preset_enum import (
    DeviceCurrentPresetEnum,
)
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class GetClimatePresetsDto(CustomModel):
    """DTO to get the possible presets of a climate."""

    presets: list[DeviceCurrentPresetEnum]
    has_ecov_mode: bool
