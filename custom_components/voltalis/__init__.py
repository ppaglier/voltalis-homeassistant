""""""

import logging

from homeassistant import config_entries
from homeassistant.core import HomeAssistant

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator
from custom_components.voltalis.lib.infrastructure.date_provider_real import DateProviderReal
from custom_components.voltalis.lib.infrastructure.voltalis_client_aiohttp import VoltalisClientAiohttp

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)


async def async_setup_entry(hass: HomeAssistant, entry: config_entries.ConfigEntry) -> bool:
    """Setup via Config Flow UI."""

    username = entry.data["username"]
    password = entry.data["password"]

    hass.data.setdefault(DOMAIN, {})

    date_provider = DateProviderReal()

    async with VoltalisClientAiohttp(
        username=username,
        password=password,
    ) as client:
        await client.login()
        await client.get_me()

        coordinator = VoltalisCoordinator(hass, client, date_provider)

        await coordinator.async_config_entry_first_refresh()

        # ✅ store coordinator for other platforms
        hass.data[DOMAIN]["coordinator"] = coordinator

        # forward setup to sensor platform
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True
