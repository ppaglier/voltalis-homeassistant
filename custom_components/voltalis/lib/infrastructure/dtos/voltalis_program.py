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

        name = self.name

        mapping = {
            "quicksettings.longleave": "quicksettings-longleave",
            "quicksettings.shortleave": "quicksettings-shortleave",
            "quicksettings.athome": "quicksettings-athome",
        }

        if name in mapping:
            name = mapping[name]

        return VoltalisProgram(
            id=self.id,
            name=name,
            type=_type,
            enabled=self.enabled,
        )


class VoltalisProgramUpdateDto(CustomModel):
    """Voltalis Program Update DTO."""

    name: str
    enabled: bool
