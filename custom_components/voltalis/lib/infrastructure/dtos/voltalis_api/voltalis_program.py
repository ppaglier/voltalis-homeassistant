from custom_components.voltalis.lib.domain.programs_management.programs.program import Program
from custom_components.voltalis.lib.domain.programs_management.programs.program_enum import ProgramTypeEnum
from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class VoltalisProgramDto(CustomModel):
    """Voltalis Program DTO."""

    id: int
    enabled: bool
    name: str

    @staticmethod
    def from_program(program: Program) -> "VoltalisProgramDto":
        """Convert from domain model"""

        name = program.name

        mapping = {
            "quicksettings-longleave": "quicksettings.longleave",
            "quicksettings-shortleave": "quicksettings.shortleave",
            "quicksettings-athome": "quicksettings.athome",
            "program-default": "program.default",
        }

        if name in mapping:
            name = mapping[name]

        return VoltalisProgramDto(
            id=program.id,
            name=name,
            enabled=program.enabled,
        )

    def to_program(self, _type: ProgramTypeEnum) -> Program:
        """Convert to domain model"""

        name = self.name

        mapping = {
            "quicksettings.longleave": "quicksettings-longleave",
            "quicksettings.shortleave": "quicksettings-shortleave",
            "quicksettings.athome": "quicksettings-athome",
            "program.default": "program-default",
        }

        if name in mapping:
            name = mapping[name]

        return Program(
            id=self.id,
            name=name,
            type=_type,
            enabled=self.enabled,
        )


class VoltalisProgramUpdateDto(CustomModel):
    """Voltalis Program Update DTO."""

    name: str
    enabled: bool
