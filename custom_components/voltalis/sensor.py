import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.base_entities.voltalis_device_entity import VoltalisDeviceEntity
from custom_components.voltalis.lib.domain.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
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
from custom_components.voltalis.lib.domain.entities.voltalis_energy_contract_info_sensor import (
    VoltalisEnergyContractInfoSensor,
)

_LOGGER = logging.getLogger(__name__)

# Limit parallel updates (the DataUpdateCoordinator already centralizes calls)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VoltalisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Voltalis sensors from a config entry."""

    device_coordinator = entry.runtime_data.coordinators.device
    health_coordinator = entry.runtime_data.coordinators.device_health
    energy_contract_coordinator = entry.runtime_data.coordinators.energy_contract

    if not device_coordinator.data:
        _LOGGER.warning("No Device data available during setup, waiting for first refresh")
        await device_coordinator.async_config_entry_first_refresh()

    sensors: dict[str, VoltalisDeviceEntity] = {}

    for device in device_coordinator.data.values():
        # Create the consumption sensor for each device
        device_consumption_sensor = VoltalisDeviceConsumptionSensor(entry, device)
        sensors[device_consumption_sensor.unique_internal_name] = device_consumption_sensor

        # Create the connected sensor for each device (if status is available)
        device_health = health_coordinator.data.get(device.id)
        if device_health is not None:
            device_connected_sensor = VoltalisDeviceConnectedSensor(entry, device)
            sensors[device_connected_sensor.unique_internal_name] = device_connected_sensor

        if device.programming.mode is not None:
            device_current_mode_sensor = VoltalisDeviceCurrentModeSensor(entry, device)
            sensors[device_current_mode_sensor.unique_internal_name] = device_current_mode_sensor

        # Create the programming sensor for each device (if applicable)
        if device.programming.prog_type is not None:
            device_programming_sensor = VoltalisDeviceProgrammingSensor(entry, device)
            sensors[device_programming_sensor.unique_internal_name] = device_programming_sensor

    if not energy_contract_coordinator.data:
        _LOGGER.warning("No Energy contract data available during setup, waiting for first refresh")
        await energy_contract_coordinator.async_config_entry_first_refresh()

    energy_contract_sensors: dict[str, VoltalisEnergyContractEntity] = {}
    for energy_contract in energy_contract_coordinator.data.values():
        # Main contract info sensor
        contract_info_sensor = VoltalisEnergyContractInfoSensor(entry, energy_contract)
        energy_contract_sensors[contract_info_sensor.unique_internal_name] = contract_info_sensor

    async_add_entities(sensors.values(), update_before_add=True)
    _LOGGER.info(f"Added {len(sensors)} Voltalis sensor entities: {list(sensors.keys())}")
