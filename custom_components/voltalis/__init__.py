"""Initialization of the Voltalis integration."""

import logging

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.config_entry_data import (
    VoltalisConfigEntry,
    VoltalisConfigEntryData,
    VoltalisCoordinators,
)
from custom_components.voltalis.lib.domain.coordinators.device import VoltalisDeviceCoordinator
from custom_components.voltalis.lib.domain.coordinators.device_daily_consumption import (
    VoltalisDeviceDailyConsumptionCoordinator,
)
from custom_components.voltalis.lib.domain.coordinators.device_health import VoltalisDeviceHealthCoordinator
from custom_components.voltalis.lib.domain.coordinators.energy_contract import VoltalisEnergyContractCoordinator
from custom_components.voltalis.lib.infrastructure.providers.date_provider_real import DateProviderReal
from custom_components.voltalis.lib.infrastructure.providers.voltalis_client_aiohttp import VoltalisClientAiohttp
from custom_components.voltalis.lib.infrastructure.repositories.voltalis_repository_voltalis_api import (
    VoltalisRepositoryVoltalisApi,
)

PLATFORMS = [
    Platform.SENSOR,
    Platform.SELECT,
    Platform.CLIMATE,
    Platform.WATER_HEATER,
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

    voltalis_client = VoltalisClientAiohttp(session=async_get_clientsession(hass))

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    await voltalis_client.login(
        username=username,
        password=password,
    )

    voltalis_repository = VoltalisRepositoryVoltalisApi(http_client=voltalis_client)

    coordinators = VoltalisCoordinators(
        device=VoltalisDeviceCoordinator(
            hass=hass,
            voltalis_repository=voltalis_repository,
            entry=entry,
        ),
        device_health=VoltalisDeviceHealthCoordinator(
            hass=hass,
            voltalis_repository=voltalis_repository,
            entry=entry,
        ),
        device_consumption=VoltalisDeviceDailyConsumptionCoordinator(
            hass=hass,
            voltalis_repository=voltalis_repository,
            date_provider=date_provider,
            entry=entry,
        ),
        energy_contract=VoltalisEnergyContractCoordinator(
            hass=hass,
            voltalis_repository=voltalis_repository,
            entry=entry,
        ),
    )

    await coordinators.setup_all()

    # ✅ store coordinator for other platforms
    entry.runtime_data = VoltalisConfigEntryData(
        voltalis_client=voltalis_client,
        date_provider=date_provider,
        coordinators=coordinators,
    )

    # forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: VoltalisConfigEntry) -> bool:
    """Unload a config entry."""

    # Stop time tracking for consumption coordinator
    entry.runtime_data.coordinators.device_consumption.stop_time_tracking()

    await entry.runtime_data.voltalis_client.logout()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    return unload_ok
