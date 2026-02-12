from custom_components.voltalis.lib.application.devices_management.queries.get_water_heater_current_operation_query import (  # noqa: E501
    GetWaterHeaterCurrentOperationQuery,
)
from custom_components.voltalis.lib.domain.devices_management.water_heaters.water_heater_operations_enum import (
    WaterHeaterOperationsEnum,
)
from custom_components.voltalis.lib.domain.voltalis_programs_management.programs.program_enum import ProgramTypeEnum


class GetWaterHeaterCurrentOperationHandler:
    """Handler to get the health of the devices."""

    def handle(self, query: GetWaterHeaterCurrentOperationQuery) -> WaterHeaterOperationsEnum:
        """Handle the request to get the health of the devices."""

        # Check if device is off
        if query.is_on is False:
            return WaterHeaterOperationsEnum.OFF

        # Check if device is off
        if query.prog_type == ProgramTypeEnum.MANUAL:
            return WaterHeaterOperationsEnum.ON

        # DEFAULT or USER planning means AUTO mode
        return WaterHeaterOperationsEnum.AUTO
