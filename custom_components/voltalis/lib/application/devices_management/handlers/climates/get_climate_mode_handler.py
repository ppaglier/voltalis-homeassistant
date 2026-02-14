from homeassistant.components.climate.const import HVACMode

from custom_components.voltalis.lib.application.devices_management.queries.get_climate_mode_query import (
    GetClimateModeQuery,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum


class GetClimateModeHandler:
    """Handler to get the current action of a climate device."""

    def handle(self, query: GetClimateModeQuery) -> HVACMode:
        """Handle the query to get the current action of a climate device."""

        if not query.is_on:
            return HVACMode.OFF

        # Check programming type to determine mode
        if query.prog_type == ProgramTypeEnum.MANUAL:
            return HVACMode.HEAT

        # DEFAULT or USER planning means AUTO mode
        return HVACMode.AUTO
