from homeassistant import config_entries

from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator
from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.infrastructure.voltalis_client_aiohttp import VoltalisClientAiohttp


class VoltalisConfigEntryData(CustomModel):
    """Config entry for the Voltalis data"""

    voltalis_client: VoltalisClientAiohttp
    coordinator: VoltalisCoordinator


VoltalisConfigEntry = config_entries.ConfigEntry[VoltalisConfigEntryData]
