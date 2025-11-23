"""Platform for Voltalis climate integration."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.voltalis_water_heater import VoltalisWaterHeater
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceTypeEnum
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

    water_heater_entities: dict[str, VoltalisEntity] = {}

    for data in coordinator.data.values():
        device: VoltalisDevice = data.device

        # Only create climate entities for heater devices
        if device.type == VoltalisDeviceTypeEnum.WATER_HEATER:
            water_heater_entity = VoltalisWaterHeater(entry, device)
            water_heater_entities[water_heater_entity.unique_internal_name] = water_heater_entity

    async_add_entities(water_heater_entities.values(), update_before_add=True)
    _LOGGER.info(
        f"Added {len(water_heater_entities)} Voltalis water heater entities: {list(water_heater_entities.keys())}"
    )
