from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class LiveConsumption(CustomModel):
    """Class to represent live consumption"""

    consumption: float
