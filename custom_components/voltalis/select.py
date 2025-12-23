import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.base_entities.voltalis_device_entity import VoltalisDeviceEntity
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.voltalis_device_preset_select import VoltalisDevicePresetSelect

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

    if not device_coordinator.data:
        _LOGGER.warning("No Voltalis data available during setup, waiting for first refresh")
        await device_coordinator.async_config_entry_first_refresh()

    selects: dict[str, VoltalisDeviceEntity] = {}

    for device in device_coordinator.data.values():
        # Create the program select entity
        device_preset_select = VoltalisDevicePresetSelect(entry, device)
        selects[device_preset_select.unique_internal_name] = device_preset_select

    async_add_entities(selects.values(), update_before_add=True)
    _LOGGER.info(f"Added {len(selects)} Voltalis select entities: {list(selects.keys())}")
