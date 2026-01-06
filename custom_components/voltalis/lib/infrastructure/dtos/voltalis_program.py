from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.models.device import VoltalisDeviceProgTypeEnum
from custom_components.voltalis.lib.domain.models.program import VoltalisProgram


class VoltalisProgramDto(CustomModel):
    """Voltalis Program DTO."""

    id: int
    enabled: bool
    name: str

    def to_voltalis_program(self, _type: VoltalisDeviceProgTypeEnum) -> VoltalisProgram:
        """Convert to domain model"""

        return VoltalisProgram(
            id=self.id,
            name=self.name,
            type=_type,
            enabled=self.enabled,
        )
