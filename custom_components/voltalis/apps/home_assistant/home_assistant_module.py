import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import (
    VoltalisConfigEntry,
    VoltalisConfigEntryData,
    VoltalisCoordinators,
)
from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.infrastructure.providers.date_provider_real import DateProviderReal
from custom_components.voltalis.lib.infrastructure.providers.voltalis_client_aiohttp import VoltalisClientAiohttp
from custom_components.voltalis.lib.infrastructure.providers.voltalis_provider_voltalis_api import (
    VoltalisProviderVoltalisApi,
)
from custom_components.voltalis.lib.voltalis_module import VoltalisModule


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
        self._voltalis_client = VoltalisClientAiohttp(session=async_get_clientsession(hass))

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        super().__init__(
            # Providers
            date_provider=DateProviderReal(),
            logger=logger,
            voltalis_provider=VoltalisProviderVoltalisApi(http_client=self._voltalis_client),
        )

        # Initialize the Home Assistant specific setup
        self.hass = hass
        self.entry = entry

        self.hass.data.setdefault(DOMAIN, {})

        username = self.entry.data["username"]
        password = self.entry.data["password"]

        await self._voltalis_client.login(
            username=username,
            password=password,
        )

        self._coordinators = VoltalisCoordinators(
            hass=self.hass,
            entry=self.entry,
            voltalis_provider=self.voltalis_provider,
            date_provider=self.date_provider,
        )

        # ✅ store coordinator for other platforms
        self.entry.runtime_data = VoltalisConfigEntryData(
            date_provider=self.date_provider,
            coordinators=self._coordinators,
            home_assistant_module=self,
        )

        await self._coordinators.setup_all()

        # forward setup to sensor platform
        await self.hass.config_entries.async_forward_entry_setups(self.entry, self.PLATFORMS)

        self.setup_handlers()

        return True

    async def async_unload_entry(self) -> bool:
        """Unload the module."""

        await self._coordinators.unload_all()

        await self._voltalis_client.logout()

        unload_ok = await self.hass.config_entries.async_unload_platforms(self.entry, self.PLATFORMS)
        return unload_ok
