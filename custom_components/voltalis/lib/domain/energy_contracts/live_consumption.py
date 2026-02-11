from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class VoltalisLiveConsumption(CustomModel):
    """Class to represent Voltalis live consumption"""

    consumption: float
