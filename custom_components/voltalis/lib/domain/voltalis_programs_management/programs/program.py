from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel
from custom_components.voltalis.lib.domain.voltalis_programs_management.programs.program_enum import ProgramTypeEnum


class Program(CustomModel):
    """Class to represent a program"""

    id: int
    type: ProgramTypeEnum
    name: str
    enabled: bool
