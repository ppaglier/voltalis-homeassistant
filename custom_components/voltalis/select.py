import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_base_entity import VoltalisBaseEntity
from custom_components.voltalis.lib.domain.entities.device_entities.voltalis_device_preset_select import (
    VoltalisDevicePresetSelect,
)
from custom_components.voltalis.lib.domain.entities.voltalis_program_select import VoltalisProgramSelect

_LOGGER = logging.getLogger(__name__)

# Limit parallel updates (the DataUpdateCoordinator already centralizes calls)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VoltalisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Voltalis select entities from a config entry."""

    device_coordinator = entry.runtime_data.coordinators.device

    select_entities: list[VoltalisBaseEntity] = []

    for device in device_coordinator.data.values():
        # Create the program select entity
        select_entities.append(VoltalisDevicePresetSelect(entry, device))

    select_entities.append(VoltalisProgramSelect(entry))

    all_entities: dict[str, VoltalisBaseEntity] = {sensor.unique_internal_name: sensor for sensor in select_entities}
    async_add_entities(all_entities.values(), update_before_add=True)
    _LOGGER.info(f"Added {len(all_entities)} Voltalis select entities: {list(all_entities.keys())}")
