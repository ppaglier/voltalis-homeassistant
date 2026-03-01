from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_base_entity import (
    VoltalisBaseEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.apps.home_assistant.entities.device_entities.voltalis_device_switch import (
    VoltalisDeviceSwitch,
)

# Limit parallel updates (the DataUpdateCoordinator already centralizes calls)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VoltalisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Voltalis switch entities from a config entry."""

    voltalis_home_assistant_module = entry.runtime_data.voltalis_home_assistant_module
    device_coordinator = voltalis_home_assistant_module.device_coordinator

    switch_entities: list[VoltalisBaseEntity] = []

    for device in device_coordinator.data.values():
        # Create switch entity for device on/off state
        switch_entities.append(VoltalisDeviceSwitch(entry, device))

    all_entities: dict[str, VoltalisBaseEntity] = {sensor.unique_internal_name: sensor for sensor in switch_entities}
    async_add_entities(all_entities.values(), update_before_add=True)
    voltalis_home_assistant_module.logger.info(
        f"Added {len(all_entities)} Voltalis switch entities: {list(all_entities.keys())}"
    )
