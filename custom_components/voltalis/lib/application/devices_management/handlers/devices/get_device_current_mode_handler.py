from custom_components.voltalis.lib.application.devices_management.queries.get_device_current_mode_query import (
    GetDeviceCurrentModeQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.modes.device_current_mode_enum import (
    DeviceCurrentModeEnum,
)


class GetDeviceCurrentModeHandler:
    """Handler to get the health of the devices."""

    def handle(self, query: GetDeviceCurrentModeQuery) -> DeviceCurrentModeEnum | None:
        """Handle the request to get the health of the devices."""

        # Check if device is off
        if query.is_on is False:
            return DeviceCurrentModeEnum.OFF

        mode_mapping = {
            DeviceModeEnum.CONFORT: DeviceCurrentModeEnum.COMFORT,
            DeviceModeEnum.ECO: DeviceCurrentModeEnum.ECO,
            DeviceModeEnum.ECOV: DeviceCurrentModeEnum.ECO,
            DeviceModeEnum.HORS_GEL: DeviceCurrentModeEnum.AWAY,
            DeviceModeEnum.TEMPERATURE: DeviceCurrentModeEnum.TEMPERATURE,
            DeviceModeEnum.NORMAL: DeviceCurrentModeEnum.ON,
        }

        mode = mode_mapping.get(query.mode, DeviceCurrentModeEnum.OFF)  # Default to OFF if preset is unrecognized
        return mode
