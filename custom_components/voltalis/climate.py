"""Platform for Voltalis climate integration."""

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.device import VoltalisDevice, VoltalisDeviceTypeEnum
from custom_components.voltalis.lib.domain.entities.voltalis_climate import VoltalisClimate
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)

# Limit parallel updates (the DataUpdateCoordinator already centralizes calls)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VoltalisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Voltalis climate entities from a config entry."""

    coordinator = entry.runtime_data.coordinator

    if not coordinator.data:
        _LOGGER.warning("No Voltalis data available during setup, waiting for first refresh")
        await coordinator.async_config_entry_first_refresh()

    climate_entities: list[VoltalisEntity] = []

    for data in coordinator.data.values():
        device: VoltalisDevice = data.device

        # Only create climate entities for heater devices
        if device.type == VoltalisDeviceTypeEnum.HEATER:
            climate_entity = VoltalisClimate(entry, device)
            climate_entities.append(climate_entity)
            _LOGGER.debug("Created climate entity for device %s", device.name)

    async_add_entities(climate_entities, update_before_add=True)
    _LOGGER.info("Added %d Voltalis climate entities", len(climate_entities))

    # Register service actions
    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        "set_manual_mode",
        {
            vol.Optional("preset_mode"): cv.string,
            vol.Optional("temperature"): vol.Coerce(float),
            vol.Optional("duration_hours"): lambda v: None if v is None else cv.positive_int(v),
        },
        "async_service_set_manual_mode",
    )

    platform.async_register_entity_service(
        "disable_manual_mode",
        {},
        "async_service_disable_manual_mode",
    )

    platform.async_register_entity_service(
        "set_quick_boost",
        {
            vol.Optional("duration_hours", default=2): vol.Coerce(float),
            vol.Optional("temperature"): vol.Coerce(float),
        },
        "async_service_set_quick_boost",
    )
