from homeassistant import config_entries

from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator
from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.services import VoltalisServiceHandler


class VoltalisConfigEntryData(CustomModel):
    """Config entry for the Voltalis data"""

    coordinator: VoltalisCoordinator
    service_handler: VoltalisServiceHandler


VoltalisConfigEntry = config_entries.ConfigEntry[VoltalisConfigEntryData]
