import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.device import VoltalisDevice
from custom_components.voltalis.lib.domain.sensors.voltalis_connected_sensor import VoltalisConnectedSensor
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

    sensors: list[VoltalisEntity] = []

    for data in coordinator.data.values():
        # Ignore devices data that didn't have status
        if data.status is None:
            continue
        device: VoltalisDevice = data.device

        # Create the connected sensor for each device
        connected_sensor = VoltalisConnectedSensor(coordinator, device)
        sensors.append(connected_sensor)

        _LOGGER.debug("Created connected sensor for device %s", device.name)

    async_add_entities(sensors, update_before_add=True)
    _LOGGER.info("Added %d Voltalis connected sensors", len(sensors))
