"""Platform for Voltalis water heater integration."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.voltalis_water_heater import VoltalisWaterHeater
from custom_components.voltalis.lib.domain.models.device import VoltalisDeviceTypeEnum
from custom_components.voltalis.lib.domain.voltalis_device_entity import VoltalisDeviceEntity

_LOGGER = logging.getLogger(__name__)

# Limit parallel updates (the DataUpdateCoordinator already centralizes calls)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VoltalisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Voltalis water heater entities from a config entry."""

    device_coordinator = entry.runtime_data.coordinators.device

    if not device_coordinator.data:
        _LOGGER.warning("No Voltalis data available during setup, waiting for first refresh")
        await device_coordinator.async_config_entry_first_refresh()

    water_heater_entities: dict[str, VoltalisDeviceEntity] = {}

    for device in device_coordinator.data.values():
        # Only create water heater entities for water heater devices
        if device.type == VoltalisDeviceTypeEnum.WATER_HEATER:
            water_heater_entity = VoltalisWaterHeater(entry, device)
            water_heater_entities[water_heater_entity.unique_internal_name] = water_heater_entity

    async_add_entities(water_heater_entities.values(), update_before_add=True)
    _LOGGER.info(
        f"Added {len(water_heater_entities)} Voltalis water heater entities: {list(water_heater_entities.keys())}"
    )
