from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class LivePower(CustomModel):
    """Class to represent live consumption"""

    power: float
