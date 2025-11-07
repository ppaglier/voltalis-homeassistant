import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.const import DOMAIN
from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator
from custom_components.voltalis.lib.domain.device import VoltalisDevice
from custom_components.voltalis.lib.domain.sensors.voltalis_consumption_sensor import VoltalisConsumptionSensor
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Voltalis sensors from a config entry."""

    coordinator: VoltalisCoordinator = hass.data[DOMAIN]["coordinator"]

    if not coordinator.data:
        _LOGGER.warning("No Voltalis data available during setup, waiting for first refresh")
        await coordinator.async_config_entry_first_refresh()

    sensors: list[VoltalisEntity] = []

    for device_id, data in coordinator.data.items():
        device: VoltalisDevice = data.device

        # Create the consumption sensor for each device
        consumption_sensor = VoltalisConsumptionSensor(coordinator, device)
        sensors.append(consumption_sensor)

        _LOGGER.debug("Created consumption sensor for device %s", device.name)

    async_add_entities(sensors)
    _LOGGER.info("Added %d Voltalis consumption sensors", len(sensors))
