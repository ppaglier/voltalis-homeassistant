from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class GetClimateModeQuery(CustomModel):
    """Query to get the current mode of a climate device."""

    is_on: bool
    prog_type: ProgramTypeEnum
