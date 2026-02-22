from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class Program(CustomModel):
    """Class to represent a program"""

    id: int
    type: ProgramTypeEnum
    name: str
    enabled: bool
