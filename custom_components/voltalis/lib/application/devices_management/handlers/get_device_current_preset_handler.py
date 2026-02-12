from custom_components.voltalis.lib.application.devices_management.queries.get_device_current_preset_query import (
    GetDeviceCurrentPresetQuery,
)
from custom_components.voltalis.lib.domain.devices_management.device.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.preset_enum import DevicePresetEnum


class GetDeviceCurrentPresetHandler:
    """Handler to get the health of the devices."""

    def handle(self, query: GetDeviceCurrentPresetQuery) -> DevicePresetEnum | None:
        """Handle the request to get the health of the devices."""

        # Check if device is off
        if query.is_on is False:
            return DevicePresetEnum.OFF

        # Check if device is off
        if query.id_manual_setting is None:
            return DevicePresetEnum.AUTO

        if query.mode is None:
            return None

        mode_mapping = {
            DeviceModeEnum.CONFORT: DevicePresetEnum.COMFORT,
            DeviceModeEnum.ECO: DevicePresetEnum.ECO,
            DeviceModeEnum.ECOV: DevicePresetEnum.ECO,
            DeviceModeEnum.HORS_GEL: DevicePresetEnum.FROST_PROTECTION,
            DeviceModeEnum.TEMPERATURE: DevicePresetEnum.TEMPERATURE,
            DeviceModeEnum.NORMAL: DevicePresetEnum.ON,
        }

        mode = mode_mapping.get(query.mode, DevicePresetEnum.OFF)  # Default to OFF if preset is unrecognized
        return mode
