from homeassistant import config_entries

from custom_components.voltalis.lib.application.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.lib.domain.coordinators.device import VoltalisDeviceCoordinator
from custom_components.voltalis.lib.domain.coordinators.device_daily_consumption import (
    VoltalisDeviceDailyConsumptionCoordinator,
)
from custom_components.voltalis.lib.domain.coordinators.device_health import VoltalisDeviceHealthCoordinator
from custom_components.voltalis.lib.domain.coordinators.energy_contract import VoltalisEnergyContractCoordinator
from custom_components.voltalis.lib.domain.coordinators.live_consumption import VoltalisLiveConsumptionCoordinator
from custom_components.voltalis.lib.domain.custom_model import CustomModel
from custom_components.voltalis.lib.infrastructure.providers.voltalis_client_aiohttp import VoltalisClientAiohttp


class VoltalisCoordinators(CustomModel):
    """Class that represent the coordinators of the integration"""

    device: VoltalisDeviceCoordinator
    device_health: VoltalisDeviceHealthCoordinator
    device_daily_consumption: VoltalisDeviceDailyConsumptionCoordinator
    live_consumption: VoltalisLiveConsumptionCoordinator
    energy_contract: VoltalisEnergyContractCoordinator

    async def setup_all(self) -> None:
        # Do first refresh for regular coordinators
        arr: list[BaseVoltalisCoordinator] = [
            self.device,
            self.device_health,
            self.device_daily_consumption,
            self.live_consumption,
            self.energy_contract,
        ]
        for coordinator in arr:
            await coordinator.async_config_entry_first_refresh()

        # For consumption, start time-based scheduling after initial refresh
        self.device_daily_consumption.start_time_tracking()
        self.live_consumption.start_time_tracking()

    async def unload_all(self) -> None:
        # Stop time tracking for consumption coordinators
        self.device_daily_consumption.stop_time_tracking()
        self.live_consumption.stop_time_tracking()


class VoltalisConfigEntryData(CustomModel):
    """Config entry for the Voltalis data"""

    voltalis_client: VoltalisClientAiohttp
    date_provider: DateProvider
    coordinators: VoltalisCoordinators


VoltalisConfigEntry = config_entries.ConfigEntry[VoltalisConfigEntryData]
