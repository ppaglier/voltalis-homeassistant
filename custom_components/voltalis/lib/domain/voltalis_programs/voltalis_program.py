from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel
from custom_components.voltalis.lib.domain.voltalis_programs.voltalis_program_enum import VoltalisDeviceProgTypeEnum


class VoltalisProgram(CustomModel):
    """Voltalis Program model."""

    id: int
    type: VoltalisDeviceProgTypeEnum
    name: str
    enabled: bool
