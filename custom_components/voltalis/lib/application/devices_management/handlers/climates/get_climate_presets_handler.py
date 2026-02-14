from custom_components.voltalis.lib.application.devices_management.dtos.get_climate_presets_dto import (
    GetClimatePresetsDto,
)
from custom_components.voltalis.lib.application.devices_management.queries.get_climate_presets_query import (
    GetClimatePresetsQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.device_current_preset_enum import (
    DeviceCurrentPresetEnum,
)


class GetClimatePresetsHandler:
    """Handler to get the possible presets of a climate."""

    def handle(self, query: GetClimatePresetsQuery) -> GetClimatePresetsDto:
        """Handle the query to get the possible presets of a device."""

        preset_mapping = {
            DeviceModeEnum.CONFORT: DeviceCurrentPresetEnum.COMFORT,
            DeviceModeEnum.ECO: DeviceCurrentPresetEnum.ECO,
            DeviceModeEnum.ECOV: DeviceCurrentPresetEnum.ECO,
            DeviceModeEnum.HORS_GEL: DeviceCurrentPresetEnum.AWAY,
            DeviceModeEnum.NORMAL: DeviceCurrentPresetEnum.OFF,
            DeviceModeEnum.TEMPERATURE: DeviceCurrentPresetEnum.OFF,
        }

        has_ecov_mode = DeviceModeEnum.ECOV in query.available_modes

        # Build preset modes from available modes
        presets: list[DeviceCurrentPresetEnum] = []
        for voltalis_mode in preset_mapping:
            ha_mode = preset_mapping.get(voltalis_mode)
            if ha_mode is None:
                continue
            # Skip NONE mode here, will add it at the end
            if ha_mode is DeviceCurrentPresetEnum.OFF:
                continue
            if voltalis_mode in query.available_modes and ha_mode not in presets:
                presets.append(ha_mode)

        return GetClimatePresetsDto(
            presets=[
                *presets,
                DeviceCurrentPresetEnum.OFF,
            ],
            has_ecov_mode=has_ecov_mode,
        )
