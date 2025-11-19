import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.voltalis_program_select import VoltalisProgramSelect
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
    """Set up Voltalis select entities from a config entry."""

    coordinator = entry.runtime_data.coordinator

    if not coordinator.data:
        _LOGGER.warning("No Voltalis data available during setup, waiting for first refresh")
        await coordinator.async_config_entry_first_refresh()

    selects: dict[str, VoltalisEntity] = {}

    for data in coordinator.data.values():
        device: VoltalisDevice = data.device

        # Create the program select entity only for heaters (not water heaters)
        if device.type == VoltalisDeviceTypeEnum.HEATER:
            program_select = VoltalisProgramSelect(entry, device)
            selects[program_select.unique_internal_name] = program_select

    async_add_entities(selects.values(), update_before_add=True)
    _LOGGER.info(f"Added {len(selects)} Voltalis select entities: {list(selects.keys())}")
