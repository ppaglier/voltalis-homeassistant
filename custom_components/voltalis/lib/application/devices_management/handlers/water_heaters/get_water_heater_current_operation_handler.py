from custom_components.voltalis.lib.application.devices_management.queries.get_water_heater_current_operation_query import (  # noqa: E501
    GetWaterHeaterCurrentOperationQuery,
)
from custom_components.voltalis.lib.domain.devices_management.water_heaters.water_heater_current_operations_enum import (  # noqa: E501
    WaterHeaterCurrentOperationEnum,
)
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum


class GetWaterHeaterCurrentOperationHandler:
    """Handler to get the health of the devices."""

    def handle(self, query: GetWaterHeaterCurrentOperationQuery) -> WaterHeaterCurrentOperationEnum:
        """Handle the request to get the health of the devices."""

        # Check if device is off
        if query.is_on is False:
            return WaterHeaterCurrentOperationEnum.OFF

        # Check if device is off
        if query.prog_type == ProgramTypeEnum.MANUAL:
            return WaterHeaterCurrentOperationEnum.ON

        # DEFAULT or USER planning means AUTO mode
        return WaterHeaterCurrentOperationEnum.AUTO
