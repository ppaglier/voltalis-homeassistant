from custom_components.voltalis.lib.application.devices_management.queries.get_device_preset_query import (
    GetDevicePresetQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.preset_enum import DeviceCurrentPresetEnum
from custom_components.voltalis.lib.domain.devices_management.presets.presets_mappings import MODE_PRESET_MAPPING
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum


class GetDevicePresetHandler:
    """Handler to get the current preset of a device."""

    def handle(self, query: GetDevicePresetQuery) -> DeviceCurrentPresetEnum | None:
        """Get the current preset of the device based on its mode and programming state."""

        # Check if device is off
        if query.is_on is False:
            return DeviceCurrentPresetEnum.OFF

        # Check if device is off
        if not query.climate_mode and query.prog_type is ProgramTypeEnum.DEFAULT:
            return DeviceCurrentPresetEnum.AUTO

        if query.mode is None:
            return None

        if query.climate_mode and query.mode in [DeviceModeEnum.TEMPERATURE, DeviceModeEnum.ON]:
            # For climate devices in TEMPERATURE mode, we consider the preset to be OFF
            return DeviceCurrentPresetEnum.OFF

        # Default to OFF if preset is unrecognized
        preset = MODE_PRESET_MAPPING.get(query.mode, DeviceCurrentPresetEnum.OFF)
        return preset
