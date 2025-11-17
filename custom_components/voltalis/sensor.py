import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.device import VoltalisDevice
from custom_components.voltalis.lib.domain.sensors.voltalis_active_program_sensor import VoltalisActiveProgramSensor
from custom_components.voltalis.lib.domain.sensors.voltalis_consumption_sensor import VoltalisConsumptionSensor
from custom_components.voltalis.lib.domain.sensors.voltalis_current_power_sensor import VoltalisCurrentPowerSensor
from custom_components.voltalis.lib.domain.sensors.voltalis_yearly_objective_sensor import VoltalisYearlyObjectiveSensor
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

    # Track if we've already added site-wide sensors (only add once)
    site_sensors_added = False

    for data in coordinator.data.values():
        device: VoltalisDevice = data.device

        # Create the consumption sensor for each device
        consumption_sensor = VoltalisConsumptionSensor(coordinator, device)
        sensors.append(consumption_sensor)
        _LOGGER.debug("Created consumption sensor for device %s", device.name)

        # Add site-wide sensors only once (they're the same for all devices)
        if not site_sensors_added:
            # Add current power sensor (real-time power consumption)
            if data.current_power is not None:
                current_power_sensor = VoltalisCurrentPowerSensor(coordinator, device)
                sensors.append(current_power_sensor)
                _LOGGER.debug("Created current power sensor")

            # Add yearly objective sensor
            if data.consumption_objective is not None:
                yearly_objective_sensor = VoltalisYearlyObjectiveSensor(coordinator, device)
                sensors.append(yearly_objective_sensor)
                _LOGGER.debug("Created yearly objective sensor")

            # Add active program sensor
            if data.programs:
                active_program_sensor = VoltalisActiveProgramSensor(coordinator, device)
                sensors.append(active_program_sensor)
                _LOGGER.debug("Created active program sensor")

            site_sensors_added = True

    async_add_entities(sensors, update_before_add=True)
    _LOGGER.info("Added %d Voltalis sensors", len(sensors))
