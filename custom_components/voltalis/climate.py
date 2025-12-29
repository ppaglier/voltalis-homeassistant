"""Platform for Voltalis climate integration."""

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_base_entity import VoltalisBaseEntity
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_device_entity import VoltalisDeviceEntity
from custom_components.voltalis.lib.domain.entities.device_entities.voltalis_climate import VoltalisClimate
from custom_components.voltalis.lib.domain.models.device import VoltalisDeviceTypeEnum

_LOGGER = logging.getLogger(__name__)

# Limit parallel updates (the DataUpdateCoordinator already centralizes calls)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VoltalisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Voltalis climate entities from a config entry."""

    device_coordinator = entry.runtime_data.coordinators.device

    if not device_coordinator.data:
        _LOGGER.warning("No Voltalis data available during setup, waiting for first refresh")
        await device_coordinator.async_config_entry_first_refresh()

    climate_entities: list[VoltalisDeviceEntity] = []

    for device in device_coordinator.data.values():
        # Only create climate entities for heater devices
        if device.type == VoltalisDeviceTypeEnum.HEATER:
            climate_entities.append(VoltalisClimate(entry, device))

    all_entities: dict[str, VoltalisBaseEntity] = {sensor.unique_internal_name: sensor for sensor in climate_entities}
    async_add_entities(all_entities.values(), update_before_add=True)
    _LOGGER.info(f"Added {len(all_entities)} Voltalis climate entities: {list(all_entities.keys())}")

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
