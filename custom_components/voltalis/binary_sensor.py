import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.device import VoltalisDevice, VoltalisDeviceTypeEnum
from custom_components.voltalis.lib.domain.entities.voltalis_connected_sensor import VoltalisConnectedSensor
from custom_components.voltalis.lib.domain.entities.voltalis_manual_mode_sensor import VoltalisManualModeSensor
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)

# Limit parallel updates (the DataUpdateCoordinator already centralizes calls)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VoltalisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Voltalis binary sensors from a config entry."""

    coordinator = entry.runtime_data.coordinator

    if not coordinator.data:
        _LOGGER.warning("No Voltalis data available during setup, waiting for first refresh")
        await coordinator.async_config_entry_first_refresh()

    sensors: list[VoltalisEntity] = []

    for data in coordinator.data.values():
        device: VoltalisDevice = data.device

        # Create the connected sensor for each device (if status is available)
        if data.status is not None:
            connected_sensor = VoltalisConnectedSensor(entry, device)
            sensors.append(connected_sensor)
            _LOGGER.debug("Created connected sensor for device %s", device.name)

        # Create manual mode sensor for heater devices
        if (
            device.type in [VoltalisDeviceTypeEnum.HEATER, VoltalisDeviceTypeEnum.WATER_HEATER]
            and data.manual_setting is not None
        ):
            manual_mode_sensor = VoltalisManualModeSensor(entry, device)
            sensors.append(manual_mode_sensor)
            _LOGGER.debug("Created manual mode sensor for device %s", device.name)

    async_add_entities(sensors, update_before_add=True)
    _LOGGER.info("Added %d Voltalis binary sensors", len(sensors))
