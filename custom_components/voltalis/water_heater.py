"""Platform for Voltalis water heater integration."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_base_entity import (
    VoltalisBaseEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_device_entity import (
    VoltalisDeviceEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.apps.home_assistant.entities.device_entities.voltalis_water_heater import (
    VoltalisWaterHeater,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceTypeEnum

# Limit parallel updates (the DataUpdateCoordinator already centralizes calls)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VoltalisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Voltalis water heater entities from a config entry."""

    voltalis_home_assistant_module = entry.runtime_data.voltalis_home_assistant_module
    device_coordinator = voltalis_home_assistant_module.device_coordinator

    water_heater_entities: list[VoltalisDeviceEntity] = []

    for device in device_coordinator.data.values():
        # Only create water heater entities for water heater devices
        if device.type == DeviceTypeEnum.WATER_HEATER:
            water_heater_entities.append(VoltalisWaterHeater(entry, device))

    all_entities: dict[str, VoltalisBaseEntity] = {
        sensor.unique_internal_name: sensor for sensor in water_heater_entities
    }
    async_add_entities(all_entities.values(), update_before_add=True)
    voltalis_home_assistant_module.logger.info(
        f"Added {len(all_entities)} Voltalis water heater entities: {list(all_entities.keys())}"
    )
