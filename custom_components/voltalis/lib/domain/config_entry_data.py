from homeassistant import config_entries

from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.coordinators.device import VoltalisDeviceCoordinator
from custom_components.voltalis.lib.domain.coordinators.device_consumption import VoltalisDeviceConsumptionCoordinator
from custom_components.voltalis.lib.domain.coordinators.device_health import VoltalisDeviceHealthCoordinator
from custom_components.voltalis.lib.domain.coordinators.device_settings import VoltalisDeviceSettingsCoordinator
from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.infrastructure.providers.voltalis_client_aiohttp import VoltalisClientAiohttp


class VoltalisCoordinators(CustomModel):
    """Class that represent the coordinators of the integration"""

    device: VoltalisDeviceCoordinator
    device_health: VoltalisDeviceHealthCoordinator
    device_settings: VoltalisDeviceSettingsCoordinator
    device_consumption: VoltalisDeviceConsumptionCoordinator

    @property
    def all(self) -> list[BaseVoltalisCoordinator]:
        """Get all coordinators as a list."""
        return [
            self.device,
            self.device_health,
            self.device_settings,
            self.device_consumption,
        ]


class VoltalisConfigEntryData(CustomModel):
    """Config entry for the Voltalis data"""

    voltalis_client: VoltalisClientAiohttp
    coordinators: VoltalisCoordinators


VoltalisConfigEntry = config_entries.ConfigEntry[VoltalisConfigEntryData]
