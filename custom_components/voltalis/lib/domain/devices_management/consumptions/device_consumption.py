from custom_components.voltalis.lib.domain.shared.custom_model import CustomModel


class DeviceConsumption(CustomModel):
    """Class to represent Voltalis devices consumption"""

    daily_consumption: float
