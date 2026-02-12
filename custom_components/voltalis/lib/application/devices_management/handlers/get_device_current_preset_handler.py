from custom_components.voltalis.lib.application.devices_management.queries.get_device_current_preset_query import (
    GetDeviceCurrentPresetQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.device_current_preset_enum import (
    DeviceCurrentPresetEnum,
)


class GetDeviceCurrentPresetHandler:
    """Handler to get the health of the devices."""

    def handle(self, query: GetDeviceCurrentPresetQuery) -> DeviceCurrentPresetEnum | None:
        """Handle the request to get the health of the devices."""

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
            DeviceModeEnum.HORS_GEL: DeviceCurrentPresetEnum.FROST_PROTECTION,
            DeviceModeEnum.TEMPERATURE: DeviceCurrentPresetEnum.TEMPERATURE,
            DeviceModeEnum.NORMAL: DeviceCurrentPresetEnum.ON,
        }

        mode = mode_mapping.get(query.mode, DeviceCurrentPresetEnum.OFF)  # Default to OFF if preset is unrecognized
        return mode
