"""Platform for Voltalis water heater integration."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_base_entity import VoltalisBaseEntity
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_device_entity import VoltalisDeviceEntity
from custom_components.voltalis.lib.domain.entities.device_entities.voltalis_water_heater import VoltalisWaterHeater
from custom_components.voltalis.lib.domain.models.device import VoltalisDeviceTypeEnum

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

    water_heater_entities: list[VoltalisDeviceEntity] = []

    for device in device_coordinator.data.values():
        # Only create water heater entities for water heater devices
        if device.type == VoltalisDeviceTypeEnum.WATER_HEATER:
            water_heater_entities.append(VoltalisWaterHeater(entry, device))

    all_entities: dict[str, VoltalisBaseEntity] = {
        sensor.unique_internal_name: sensor for sensor in water_heater_entities
    }
    async_add_entities(all_entities.values(), update_before_add=True)
    _LOGGER.info(f"Added {len(all_entities)} Voltalis water heater entities: {list(all_entities.keys())}")
