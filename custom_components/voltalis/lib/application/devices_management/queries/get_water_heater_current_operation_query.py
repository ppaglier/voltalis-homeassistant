from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel
from custom_components.voltalis.lib.domain.voltalis_programs_management.programs.program_enum import ProgramTypeEnum


class GetWaterHeaterCurrentOperationQuery(CustomModel):
    """Query to get the current operation of a water heater device."""

    is_on: bool
    prog_type: ProgramTypeEnum
