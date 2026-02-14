from custom_components.voltalis.lib.application.devices_management.queries.get_device_preset_query import (
    GetDevicePresetQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.device_current_preset_enum import (
    DeviceCurrentPresetEnum,
)


class GetDevicePresetHandler:
    """Handler to get the current preset of a device."""

    def handle(self, query: GetDevicePresetQuery) -> DeviceCurrentPresetEnum | None:
        """Get the current preset of the device based on its mode and programming state."""

        # Check if device is off
        if query.is_on is False:
            return DeviceCurrentPresetEnum.OFF

        # Check if device is off
        if query.id_manual_setting is None:
            return DeviceCurrentPresetEnum.AUTO

        if query.mode is None:
            return None

        mode_mapping = {
            DeviceModeEnum.CONFORT: DeviceCurrentPresetEnum.COMFORT,
            DeviceModeEnum.ECO: DeviceCurrentPresetEnum.ECO,
            DeviceModeEnum.ECOV: DeviceCurrentPresetEnum.ECO,
            DeviceModeEnum.HORS_GEL: DeviceCurrentPresetEnum.AWAY,
            DeviceModeEnum.TEMPERATURE: DeviceCurrentPresetEnum.TEMPERATURE,
            DeviceModeEnum.NORMAL: DeviceCurrentPresetEnum.ON,
        }

        mode = mode_mapping.get(query.mode, DeviceCurrentPresetEnum.OFF)  # Default to OFF if preset is unrecognized
        return mode
