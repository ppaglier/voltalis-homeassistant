from custom_components.voltalis.lib.application.devices_management.dtos.get_device_presets_dto import (
    GetDevicePresetsDto,
)
from custom_components.voltalis.lib.application.devices_management.queries.get_device_presets_query import (
    GetDevicePresetsQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.device_current_preset_enum import (
    DeviceCurrentPresetEnum,
)


class GetDevicePresetsHandler:
    """Handler to get the possible presets of a device."""

    def handle(self, query: GetDevicePresetsQuery) -> GetDevicePresetsDto:
        """Handle the query to get the possible presets of a device."""

        presets_config: dict[DeviceCurrentPresetEnum, list[DeviceModeEnum]] = {
            DeviceCurrentPresetEnum.AUTO: [],
            DeviceCurrentPresetEnum.ON: [DeviceModeEnum.NORMAL],
            DeviceCurrentPresetEnum.COMFORT: [DeviceModeEnum.CONFORT],
            DeviceCurrentPresetEnum.ECO: [DeviceModeEnum.ECO, DeviceModeEnum.ECOV],
            DeviceCurrentPresetEnum.AWAY: [DeviceModeEnum.HORS_GEL],
            DeviceCurrentPresetEnum.TEMPERATURE: [DeviceModeEnum.TEMPERATURE],
            DeviceCurrentPresetEnum.OFF: [],
        }

        return GetDevicePresetsDto(
            presets=[
                preset
                for (preset, modes) in presets_config.items()
                if len(modes) == 0 or any(mode in query.available_modes for mode in modes)
            ],
            has_ecov_mode=DeviceModeEnum.ECOV in query.available_modes,
            has_on_mode=DeviceModeEnum.NORMAL in query.available_modes,
        )
