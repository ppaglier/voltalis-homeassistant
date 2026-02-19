from custom_components.voltalis.lib.application.devices_management.dtos.get_device_presets_dto import (
    GetDevicePresetsDto,
)
from custom_components.voltalis.lib.application.devices_management.queries.get_device_presets_query import (
    GetDevicePresetsQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.preset_enum import DeviceCurrentPresetEnum
from custom_components.voltalis.lib.domain.devices_management.presets.presets_mappings import PRESET_MODE_MAPPING


class GetDevicePresetsHandler:
    """Handler to get the possible presets of a device."""

    def handle(self, query: GetDevicePresetsQuery) -> GetDevicePresetsDto:
        """Handle the query to get the possible presets of a device."""

        presets_config: dict[DeviceCurrentPresetEnum, DeviceModeEnum | None] = {
            DeviceCurrentPresetEnum.AUTO: None,
            **{preset: mode for preset, mode in PRESET_MODE_MAPPING.items()},
            DeviceCurrentPresetEnum.OFF: None,
        }

        # If it's a climate device, we don't include AUTO/ON/OFF/TEMPERATURE presets as they are not relevant
        if query.climate_mode:
            presets_config.pop(DeviceCurrentPresetEnum.AUTO)
            presets_config.pop(DeviceCurrentPresetEnum.ON)
            presets_config.pop(DeviceCurrentPresetEnum.TEMPERATURE)

        return GetDevicePresetsDto(
            presets=[
                preset for (preset, mode) in presets_config.items() if mode is None or mode in query.available_modes
            ],
            has_on_mode=DeviceModeEnum.ON in query.available_modes,
        )
