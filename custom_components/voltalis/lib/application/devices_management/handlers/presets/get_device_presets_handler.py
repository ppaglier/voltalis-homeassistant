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

        preset_mapping = {
            DeviceModeEnum.CONFORT: DeviceCurrentPresetEnum.COMFORT,
            DeviceModeEnum.ECO: DeviceCurrentPresetEnum.ECO,
            DeviceModeEnum.ECOV: DeviceCurrentPresetEnum.ECO,
            DeviceModeEnum.HORS_GEL: DeviceCurrentPresetEnum.AWAY,
            DeviceModeEnum.TEMPERATURE: DeviceCurrentPresetEnum.TEMPERATURE,
            DeviceModeEnum.NORMAL: DeviceCurrentPresetEnum.ON,
        }

        available_presets = set(preset_mapping[mode] for mode in query.available_modes if mode in preset_mapping)

        has_ecov_mode = DeviceModeEnum.ECOV in query.available_modes
        has_on_mode = DeviceModeEnum.NORMAL in query.available_modes

        # Build options modes from available modes
        possible_presets: list[DeviceCurrentPresetEnum] = []
        for voltalis_mode in DeviceCurrentPresetEnum:
            # Skip AUTO | ON | NONE mode here, will add it after the loop
            if voltalis_mode in [
                DeviceCurrentPresetEnum.AUTO,
                DeviceCurrentPresetEnum.ON,
                DeviceCurrentPresetEnum.OFF,
            ]:
                continue

            if voltalis_mode not in available_presets:
                # Special handling for ECOV mode
                if (has_ecov_mode and voltalis_mode != DeviceCurrentPresetEnum.ECO) or not has_ecov_mode:
                    continue
                voltalis_mode = DeviceCurrentPresetEnum.ECO

            if voltalis_mode not in possible_presets:
                possible_presets.append(voltalis_mode)

        return GetDevicePresetsDto(
            presets=[
                DeviceCurrentPresetEnum.AUTO,
                *([DeviceCurrentPresetEnum.ON] if has_on_mode else []),
                *possible_presets,
                DeviceCurrentPresetEnum.OFF,
            ],
            has_ecov_mode=has_ecov_mode,
            has_on_mode=has_on_mode,
        )
