from enum import StrEnum

from homeassistant.components.climate import PRESET_AWAY, PRESET_COMFORT, PRESET_ECO, PRESET_NONE

from custom_components.voltalis.lib.application.devices_management.queries.get_device_mode_query import (
    GetDeviceModeQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum


class DeviceCurrentModeEnum(StrEnum):
    """Enum for device presets"""

    COMFORT = PRESET_COMFORT
    ECO = PRESET_ECO
    AWAY = PRESET_AWAY
    TEMPERATURE = "temperature"

    ON = "on"
    OFF = PRESET_NONE
    AUTO = "auto"


class GetDeviceModeHandler:
    """Handler for getting the current device mode based on its state and program type."""

    def handle(self, query: GetDeviceModeQuery) -> DeviceCurrentModeEnum | None:
        """Determine the current device mode based on the query parameters."""

        # Check if device is off
        if query.is_on is False:
            return DeviceCurrentModeEnum.OFF

        mode_mapping = {
            DeviceModeEnum.COMFORT: DeviceCurrentModeEnum.COMFORT,
            DeviceModeEnum.ECO: DeviceCurrentModeEnum.ECO,
            DeviceModeEnum.AWAY: DeviceCurrentModeEnum.AWAY,
            DeviceModeEnum.TEMPERATURE: DeviceCurrentModeEnum.TEMPERATURE,
            DeviceModeEnum.ON: DeviceCurrentModeEnum.ON,
        }

        mode = mode_mapping.get(query.mode, DeviceCurrentModeEnum.OFF)  # Default to OFF if preset is unrecognized
        return mode
