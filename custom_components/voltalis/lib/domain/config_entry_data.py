from homeassistant import config_entries

from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator
from custom_components.voltalis.lib.domain.custom_model import CustomModel


class VoltalisConfigEntryData(CustomModel):
    """Config entry for the Voltalis data"""

    coordinator: VoltalisCoordinator


VoltalisConfigEntry = config_entries.ConfigEntry[VoltalisConfigEntryData]
