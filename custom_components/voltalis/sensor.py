import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.voltalis_device_connected_sensor import (
    VoltalisDeviceConnectedSensor,
)
from custom_components.voltalis.lib.domain.entities.voltalis_device_consumption_sensor import (
    VoltalisDeviceConsumptionSensor,
)
from custom_components.voltalis.lib.domain.entities.voltalis_device_current_mode_sensor import (
    VoltalisDeviceCurrentModeSensor,
)
from custom_components.voltalis.lib.domain.entities.voltalis_device_programming_sensor import (
    VoltalisDeviceProgrammingSensor,
)
from custom_components.voltalis.lib.domain.entities.voltalis_contract_info_sensor import (
    VoltalisContractInfoSensor,
)
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice
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

    # Fetch contracts once at setup
    try:
        await coordinator.async_fetch_contracts()
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Failed to fetch subscriber contracts during setup: %s", err)

    sensors: dict[str, VoltalisEntity] = {}

    for data in coordinator.data.values():
        device: VoltalisDevice = data.device

        # Create the consumption sensor for each device
        device_consumption_sensor = VoltalisDeviceConsumptionSensor(entry, device)
        sensors[device_consumption_sensor.unique_internal_name] = device_consumption_sensor

        # Create the connected sensor for each device (if status is available)
        if data.health is not None:
            device_connected_sensor = VoltalisDeviceConnectedSensor(entry, device)
            sensors[device_connected_sensor.unique_internal_name] = device_connected_sensor

        if device.programming.mode is not None:
            device_current_mode_sensor = VoltalisDeviceCurrentModeSensor(entry, device)
            sensors[device_current_mode_sensor.unique_internal_name] = device_current_mode_sensor

        # Create the programming sensor for each device (if applicable)
        if device.programming.prog_type is not None:
            device_programming_sensor = VoltalisDeviceProgrammingSensor(entry, device)
            sensors[device_programming_sensor.unique_internal_name] = device_programming_sensor

    # Create contract sensors
    for contract in coordinator.contracts:
        # Main contract info sensor
        contract_info_sensor = VoltalisContractInfoSensor(entry, contract)
        sensors[contract_info_sensor.unique_internal_name] = contract_info_sensor
    async_add_entities(sensors.values(), update_before_add=True)
    _LOGGER.info(f"Added {len(sensors)} Voltalis sensor entities: {list(sensors.keys())}")
