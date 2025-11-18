import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.device import VoltalisDevice, VoltalisDeviceTypeEnum
from custom_components.voltalis.lib.domain.sensors.voltalis_consumption_sensor import VoltalisConsumptionSensor
from custom_components.voltalis.lib.domain.sensors.device.voltalis_heating_level_sensor import VoltalisHeatingLevelSensor
from custom_components.voltalis.lib.domain.sensors.device.voltalis_default_temperature_sensor import VoltalisDefaultTemperatureSensor
from custom_components.voltalis.lib.domain.sensors.device.voltalis_programming_type_sensor import VoltalisProgrammingTypeSensor
from custom_components.voltalis.lib.domain.sensors.device.voltalis_programming_name_sensor import VoltalisProgrammingNameSensor
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
        device: VoltalisDevice = data.device

        # Create the consumption sensor for each device
        consumption_sensor = VoltalisConsumptionSensor(coordinator, device)
        sensors.append(consumption_sensor)
        _LOGGER.debug("Created consumption sensor for device %s", device.name)

        # Create additional sensors for heater devices
        if device.type == VoltalisDeviceTypeEnum.HEATER:
            # Heating level sensor (only for heaters with heating_level data)
            if device.heating_level is not None:
                sensors.append(VoltalisHeatingLevelSensor(coordinator, device))
                _LOGGER.debug("Created heating level sensor for device %s", device.name)

            # Default temperature sensor
            if device.programming and device.programming.default_temperature is not None:
                sensors.append(VoltalisDefaultTemperatureSensor(coordinator, device))
                _LOGGER.debug("Created default temperature sensor for device %s", device.name)

            # Programming type sensor
            if device.programming and device.programming.prog_type:
                sensors.append(VoltalisProgrammingTypeSensor(coordinator, device))
                _LOGGER.debug("Created programming type sensor for device %s", device.name)

            # Programming name sensor
            if device.programming and device.programming.prog_name:
                sensors.append(VoltalisProgrammingNameSensor(coordinator, device))
                _LOGGER.debug("Created programming name sensor for device %s", device.name)

    async_add_entities(sensors, update_before_add=True)
    _LOGGER.info("Added %d Voltalis sensors", len(sensors))
