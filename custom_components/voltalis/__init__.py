""""""

import logging

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.coordinators.consumption_coordinator import VoltalisConsumptionCoordinator
from custom_components.voltalis.lib.infrastructure.voltalis_client_aiohttp import VoltalisClientAiohttp

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    """Setup via Config Flow UI."""

    username = entry.data["username"]
    password = entry.data["password"]

    hass.data.setdefault(DOMAIN, {})

    async with VoltalisClientAiohttp(
        username=username,
        password=password,
    ) as client:
        await client.login()

        coordinator = VoltalisConsumptionCoordinator(hass, client)

        await coordinator.async_config_entry_first_refresh()

    return True
