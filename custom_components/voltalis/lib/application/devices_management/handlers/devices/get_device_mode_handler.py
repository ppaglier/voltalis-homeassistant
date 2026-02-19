from custom_components.voltalis.lib.application.devices_management.queries.get_device_mode_query import (
    GetDeviceModeQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.modes.device_current_mode_enum import (
    DeviceCurrentModeEnum,
)


class GetDeviceModeHandler:
    """Handler to get the health of the devices."""

    def handle(self, query: GetDeviceModeQuery) -> DeviceCurrentModeEnum | None:
        """Handle the request to get the health of the devices."""

        # Check if device is off
        if query.is_on is False:
            return DeviceCurrentModeEnum.OFF

        mode_mapping = {
            DeviceModeEnum.COMFORT: DeviceCurrentModeEnum.COMFORT,
            DeviceModeEnum.ECO: DeviceCurrentModeEnum.ECO,
            DeviceModeEnum.ECOV: DeviceCurrentModeEnum.ECO,
            DeviceModeEnum.AWAY: DeviceCurrentModeEnum.AWAY,
            DeviceModeEnum.TEMPERATURE: DeviceCurrentModeEnum.TEMPERATURE,
            DeviceModeEnum.ON: DeviceCurrentModeEnum.ON,
        }

        mode = mode_mapping.get(query.mode, DeviceCurrentModeEnum.OFF)  # Default to OFF if preset is unrecognized
        return mode
