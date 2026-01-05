"""Platform for Voltalis program switch entities."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.voltalis_program_switch import VoltalisProgramSwitch

_LOGGER = logging.getLogger(__name__)

# Limit parallel updates (the DataUpdateCoordinator already centralizes calls)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VoltalisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Voltalis program switches from a config entry."""

    program_coordinator = entry.runtime_data.coordinators.program

    if not program_coordinator.data:
        _LOGGER.warning("No Voltalis program data available during setup, waiting for first refresh")
        await program_coordinator.async_config_entry_first_refresh()

    switches: dict[str, VoltalisProgramSwitch] = {}

    for program in program_coordinator.data.values():
        program_switch = VoltalisProgramSwitch(entry, program, program_coordinator)
        switches[program_switch.unique_internal_name] = program_switch

    async_add_entities(switches.values(), update_before_add=True)
    _LOGGER.info(f"Added {len(switches)} Voltalis program switch entities: {list(switches.keys())}")

