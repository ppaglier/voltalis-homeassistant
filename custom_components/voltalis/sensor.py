import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.voltalis_connected_sensor import VoltalisConnectedSensor
from custom_components.voltalis.lib.domain.entities.voltalis_consumption_sensor import VoltalisConsumptionSensor
from custom_components.voltalis.lib.domain.entities.voltalis_programming_type_sensor import (
    VoltalisProgrammingTypeSensor,
)
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
    """Set up Voltalis sensors from a config entry."""

    coordinator = entry.runtime_data.coordinator

    if not coordinator.data:
        _LOGGER.warning("No Voltalis data available during setup, waiting for first refresh")
        await coordinator.async_config_entry_first_refresh()

    sensors: dict[str, VoltalisEntity] = {}

    for data in coordinator.data.values():
        device: VoltalisDevice = data.device

        # Create the consumption sensor for each device
        consumption_sensor = VoltalisConsumptionSensor(entry, device)
        sensors[consumption_sensor.unique_internal_name] = consumption_sensor

        # Create the connected sensor for each device (if status is available)
        if data.health is not None:
            connected_sensor = VoltalisConnectedSensor(entry, device)
            sensors[connected_sensor.unique_internal_name] = connected_sensor

        # Create additional sensors for heater devices
        if device.type in [VoltalisDeviceTypeEnum.HEATER, VoltalisDeviceTypeEnum.WATER_HEATER]:
            # Default temperature sensor
            if device.programming:
                # Programming type sensor
                if device.programming.prog_type:
                    programming_type_sensor = VoltalisProgrammingTypeSensor(entry, device)
                    sensors[programming_type_sensor.unique_internal_name] = programming_type_sensor

    async_add_entities(sensors.values(), update_before_add=True)
    _LOGGER.info(f"Added {len(sensors)} Voltalis sensor entities: {list(sensors.keys())}")
