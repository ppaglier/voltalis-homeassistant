from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class VoltalisDeviceConsumption(CustomModel):
    """Class to represent Voltalis devices consumption"""

    daily_consumption: float
