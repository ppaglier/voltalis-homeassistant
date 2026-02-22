import asyncio
import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

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
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import (
    VoltalisConfigEntry,
    VoltalisConfigEntryData,
)
from custom_components.voltalis.const import (
    CONF_CLIMATE_MAX_TEMP,
    CONF_CLIMATE_MIN_TEMP,
    CONF_DEFAULT_AWAY_TEMP,
    CONF_DEFAULT_COMFORT_TEMP,
    CONF_DEFAULT_ECO_TEMP,
    CONF_DEFAULT_TEMP,
    CONF_DEFAULT_WATER_HEATER_TEMP,
    CONF_LOG_LEVEL,
    DEFAULT_AWAY_TEMP,
    DEFAULT_CLIMATE_MAX_TEMP,
    DEFAULT_CLIMATE_MIN_TEMP,
    DEFAULT_COMFORT_TEMP,
    DEFAULT_ECO_TEMP,
    DEFAULT_LOG_LEVEL,
    DEFAULT_TEMP,
    DEFAULT_WATER_HEATER_TEMP,
    DOMAIN,
    VOLTALIS_API_BASE_URL,
    LogLevelEnum,
)
from custom_components.voltalis.lib.infrastructure.providers.date_provider_real import DateProviderReal
from custom_components.voltalis.lib.infrastructure.providers.voltalis_client_aiohttp import VoltalisClientAiohttp
from custom_components.voltalis.lib.infrastructure.providers.voltalis_provider_voltalis_api import (
    VoltalisProviderVoltalisApi,
)
from custom_components.voltalis.lib.voltalis_module import VoltalisModule, VoltalisModuleConfig


class VoltalisHomeAssistantModule(VoltalisModule):
    """Module to initialize the API using FastAPI."""

    PLATFORMS = [
        Platform.SENSOR,
        Platform.SELECT,
        Platform.CLIMATE,
        Platform.WATER_HEATER,
        Platform.SWITCH,
    ]

    def __init__(self) -> None:
        """
        We can't do anything in the constructor,
        as we need to initialize the module asynchronously in async_setup_entry.
        """
        pass

    async def async_setup_entry(self, *, hass: HomeAssistant, entry: VoltalisConfigEntry) -> bool:
        """Initialize the module. used in async_setup_entry"""

        # Initialize the module
        self._voltalis_client = VoltalisClientAiohttp(
            session=async_get_clientsession(hass),
            base_url=VOLTALIS_API_BASE_URL,
        )

        logger = logging.getLogger("voltalis-home_assistant")

        log_level: LogLevelEnum = entry.options.get(CONF_LOG_LEVEL, DEFAULT_LOG_LEVEL)
        log_level_mapping = {
            LogLevelEnum.DEBUG: logging.DEBUG,
            LogLevelEnum.INFO: logging.INFO,
            LogLevelEnum.WARNING: logging.WARNING,
            LogLevelEnum.ERROR: logging.ERROR,
            LogLevelEnum.CRITICAL: logging.CRITICAL,
        }
        logger.setLevel(log_level_mapping.get(log_level, logging.INFO))

        super().__init__(
            # Providers
            date_provider=DateProviderReal(),
            logger=logger,
            voltalis_provider=VoltalisProviderVoltalisApi(http_client=self._voltalis_client),
            config=VoltalisModuleConfig(
                climate_min_temp=entry.options.get(CONF_CLIMATE_MIN_TEMP, DEFAULT_CLIMATE_MIN_TEMP),
                climate_max_temp=entry.options.get(CONF_CLIMATE_MAX_TEMP, DEFAULT_CLIMATE_MAX_TEMP),
                default_temperature=entry.options.get(CONF_DEFAULT_TEMP, DEFAULT_TEMP),
                default_away_temp=entry.options.get(CONF_DEFAULT_AWAY_TEMP, DEFAULT_AWAY_TEMP),
                default_eco_temp=entry.options.get(CONF_DEFAULT_ECO_TEMP, DEFAULT_ECO_TEMP),
                default_comfort_temp=entry.options.get(CONF_DEFAULT_COMFORT_TEMP, DEFAULT_COMFORT_TEMP),
                default_water_heater_temp=entry.options.get(CONF_DEFAULT_WATER_HEATER_TEMP, DEFAULT_WATER_HEATER_TEMP),
            ),
        )

        self.setup_handlers()

        # Initialize the Home Assistant specific setup
        self.hass = hass
        self.entry = entry

        # ✅ store config entry data with reference to the module and coordinators
        self.entry.runtime_data = VoltalisConfigEntryData(voltalis_home_assistant_module=self)

        self.hass.data.setdefault(DOMAIN, {})

        username = self.entry.data["username"]
        password = self.entry.data["password"]

        await self._voltalis_client.login(
            username=username,
            password=password,
        )

        await self.__load_coordinators()

        # forward setup to sensor platform
        await self.hass.config_entries.async_forward_entry_setups(self.entry, self.PLATFORMS)

        return True

    async def async_unload_entry(self) -> bool:
        """Unload the module."""

        # Unload platforms FIRST before closing the client session
        unload_ok = await self.hass.config_entries.async_unload_platforms(self.entry, self.PLATFORMS)

        # Then unload coordinators
        await self.__unload_coordinators()

        # Finally, close the client session
        try:
            await self._voltalis_client.logout()
        except RuntimeError:
            # Session might already be closed, this is acceptable during cleanup
            pass

        return unload_ok

    async def __load_coordinators(self) -> None:
        """Set up all coordinators."""

        self.device_coordinator = VoltalisDeviceCoordinator(entry=self.entry)
        self.device_health_coordinator = VoltalisDeviceHealthCoordinator(entry=self.entry)
        self.device_daily_consumption_coordinator = VoltalisDeviceDailyConsumptionCoordinator(entry=self.entry)
        self.live_consumption_coordinator = VoltalisLiveConsumptionCoordinator(entry=self.entry)
        self.energy_contract_coordinator = VoltalisEnergyContractCoordinator(entry=self.entry)
        self.programs_coordinator = VoltalisProgramCoordinator(entry=self.entry)

        # Do first refresh for regular coordinators
        arr: list[BaseVoltalisCoordinator] = [
            self.device_coordinator,
            self.device_health_coordinator,
            self.device_daily_consumption_coordinator,
            self.live_consumption_coordinator,
            self.energy_contract_coordinator,
            self.programs_coordinator,
        ]

        await asyncio.gather(*(coordinator.async_config_entry_first_refresh() for coordinator in arr))

        # For consumption, start time-based scheduling after initial refresh
        self.device_daily_consumption_coordinator.start_time_tracking()
        self.live_consumption_coordinator.start_time_tracking()

    async def __unload_coordinators(self) -> None:
        """Unload all coordinators."""

        # Stop time tracking for consumption coordinators
        self.device_daily_consumption_coordinator.stop_time_tracking()
        self.live_consumption_coordinator.stop_time_tracking()
