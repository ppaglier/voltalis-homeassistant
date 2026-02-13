from homeassistant.components.climate.const import HVACAction

from custom_components.voltalis.lib.application.devices_management.queries.get_climate_current_action_query import (
    GetClimateCurrentActionQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum


class GetClimateCurrentActionHandler:
    """Handler to get the current action of a climate device."""

    def handle(self, query: GetClimateCurrentActionQuery) -> HVACAction:
        """Handle the query to get the current action of a climate device."""

        # Check if device is off
        if query.is_on is False:
            return HVACAction.OFF

        if query.mode == DeviceModeEnum.HORS_GEL:
            return HVACAction.IDLE

        return HVACAction.HEATING
