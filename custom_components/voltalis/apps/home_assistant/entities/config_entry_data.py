import asyncio
from typing import TYPE_CHECKING

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from custom_components.voltalis.apps.home_assistant.coordinators.base import BaseVoltalisCoordinator
from custom_components.voltalis.apps.home_assistant.coordinators.device import VoltalisDeviceCoordinator
from custom_components.voltalis.apps.home_assistant.coordinators.device_daily_consumption import (
    VoltalisDeviceDailyConsumptionCoordinator,
)
from custom_components.voltalis.apps.home_assistant.coordinators.device_health import VoltalisDeviceHealthCoordinator
from custom_components.voltalis.apps.home_assistant.coordinators.device_realtime_consumption import (
    VoltalisLiveConsumptionCoordinator,
)
from custom_components.voltalis.apps.home_assistant.coordinators.energy_contract import (
    VoltalisEnergyContractCoordinator,
)
from custom_components.voltalis.apps.home_assistant.coordinators.program import VoltalisProgramCoordinator
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider

# Prevent circular import for type checking
if TYPE_CHECKING:
    from custom_components.voltalis.apps.home_assistant.home_assistant_module import VoltalisHomeAssistantModule


class VoltalisConfigEntryData:
    """Config entry for the Voltalis data"""

    def __init__(
        self,
        *,
        date_provider: DateProvider,
        coordinators: "VoltalisCoordinators",
        home_assistant_module: "VoltalisHomeAssistantModule",
    ) -> None:
        self.date_provider = date_provider
        self.coordinators = coordinators
        self.home_assistant_module = home_assistant_module


VoltalisConfigEntry = config_entries.ConfigEntry[VoltalisConfigEntryData]


class VoltalisCoordinators:
    """Class that represent the coordinators of the integration"""

    def __init__(
        self,
        *,
        hass: HomeAssistant,
        entry: VoltalisConfigEntry,
        voltalis_provider: VoltalisProvider,
        date_provider: DateProvider,
    ) -> None:
        self.device = VoltalisDeviceCoordinator(
            hass=hass,
            voltalis_provider=voltalis_provider,
            entry=entry,
        )
        self.device_health = VoltalisDeviceHealthCoordinator(
            hass=hass,
            voltalis_provider=voltalis_provider,
            entry=entry,
        )
        self.device_daily_consumption = VoltalisDeviceDailyConsumptionCoordinator(
            hass=hass,
            voltalis_provider=voltalis_provider,
            date_provider=date_provider,
            entry=entry,
        )
        self.live_consumption = VoltalisLiveConsumptionCoordinator(
            hass=hass,
            voltalis_provider=voltalis_provider,
            entry=entry,
        )
        self.energy_contract = VoltalisEnergyContractCoordinator(
            hass=hass,
            voltalis_provider=voltalis_provider,
            entry=entry,
            date_provider=date_provider,
        )
        self.programs = VoltalisProgramCoordinator(
            hass=hass,
            voltalis_provider=voltalis_provider,
            entry=entry,
        )

    async def setup_all(self) -> None:
        # Do first refresh for regular coordinators
        arr: list[BaseVoltalisCoordinator] = [
            self.device,
            self.device_health,
            self.device_daily_consumption,
            self.live_consumption,
            self.energy_contract,
            self.programs,
        ]

        await asyncio.gather(*(coordinator.async_config_entry_first_refresh() for coordinator in arr))

        # For consumption, start time-based scheduling after initial refresh
        self.device_daily_consumption.start_time_tracking()
        self.live_consumption.start_time_tracking()

    async def unload_all(self) -> None:
        # Stop time tracking for consumption coordinators
        self.device_daily_consumption.stop_time_tracking()
        self.live_consumption.stop_time_tracking()
