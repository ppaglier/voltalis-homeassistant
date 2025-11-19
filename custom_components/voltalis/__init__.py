"""Initialization of the Voltalis integration."""

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry, VoltalisConfigEntryData
from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator
from custom_components.voltalis.lib.infrastructure.date_provider_real import DateProviderReal
from custom_components.voltalis.lib.infrastructure.voltalis_client_aiohttp import VoltalisClientAiohttp

PLATFORMS = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.CLIMATE,
]


async def async_setup(hass: HomeAssistant, entry: VoltalisConfigEntry) -> bool:
    """Set up the Voltalis component."""

    return True


async def async_setup_entry(hass: HomeAssistant, entry: VoltalisConfigEntry) -> bool:
    """Set up Voltalis from a config entry."""

    username = entry.data["username"]
    password = entry.data["password"]

    hass.data.setdefault(DOMAIN, {})

    date_provider = DateProviderReal()

    client = VoltalisClientAiohttp(
        username=username,
        password=password,
        session=async_get_clientsession(hass),
    )

    await client.login()

    coordinator = VoltalisCoordinator(hass, client, date_provider, entry=entry)

    await coordinator.async_config_entry_first_refresh()

    # ✅ store coordinator for other platforms
    entry.runtime_data = VoltalisConfigEntryData(coordinator=coordinator)

    # forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: VoltalisConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok
