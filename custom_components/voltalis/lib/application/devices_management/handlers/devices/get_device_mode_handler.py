from custom_components.voltalis.lib.application.devices_management.queries.get_device_mode_query import (
    GetDeviceModeQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum


class GetDeviceModeHandler:
    """Handler to get the health of the devices."""

    def handle(self, query: GetDeviceModeQuery) -> DeviceModeEnum | None:
        """Handle the request to get the health of the devices."""

        # Check if device is off
        if query.is_on is False:
            return DeviceModeEnum.OFF

        return query.mode
