from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.domain.models.device import VoltalisDeviceProgTypeEnum


class VoltalisProgram(CustomModel):
    """Voltalis Program model."""

    id: int
    type: VoltalisDeviceProgTypeEnum
    name: str
    enabled: bool
