import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_device_entity import VoltalisDeviceEntity
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.lib.domain.entities.device_entities.voltalis_device_connected_sensor import (
    VoltalisDeviceConnectedSensor,
)
from custom_components.voltalis.lib.domain.entities.device_entities.voltalis_device_consumption_sensor import (
    VoltalisDeviceConsumptionSensor,
)
from custom_components.voltalis.lib.domain.entities.device_entities.voltalis_device_current_mode_sensor import (
    VoltalisDeviceCurrentModeSensor,
)
from custom_components.voltalis.lib.domain.entities.device_entities.voltalis_device_programming_sensor import (
    VoltalisDeviceProgrammingSensor,
)
from custom_components.voltalis.lib.domain.entities.energy_contract.current_mode_sensor import (
    VoltalisEnergyContractCurrentModeSensor,
)
from custom_components.voltalis.lib.domain.entities.energy_contract.kwh_current_cost_sensor import (
    VoltalisEnergyContractKwhCurrentCostSensor,
)
from custom_components.voltalis.lib.domain.entities.energy_contract.kwh_offpeak_cost_sensor import (
    VoltalisEnergyContractKwhOffPeakCostSensor,
)
from custom_components.voltalis.lib.domain.entities.energy_contract.kwh_peak_cost_sensor import (
    VoltalisEnergyContractKwhPeakCostSensor,
)
from custom_components.voltalis.lib.domain.entities.energy_contract.subscribed_power_sensor import (
    VoltalisEnergyContractSubscribedPowerSensor,
)
from custom_components.voltalis.lib.domain.models.energy_contract import VoltalisEnergyContractTypeEnum

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
    date_provider = entry.runtime_data.date_provider

    if not device_coordinator.data:
        _LOGGER.warning("No Device data available during setup, waiting for first refresh")
        await device_coordinator.async_config_entry_first_refresh()

    device_sensors: dict[str, VoltalisDeviceEntity] = {}

    for device in device_coordinator.data.values():
        # Create the consumption sensor for each device
        device_consumption_sensor = VoltalisDeviceConsumptionSensor(entry, device)
        device_sensors[device_consumption_sensor.unique_internal_name] = device_consumption_sensor

        # Create the connected sensor for each device (if status is available)
        device_health = health_coordinator.data.get(device.id)
        if device_health is not None:
            device_connected_sensor = VoltalisDeviceConnectedSensor(entry, device)
            device_sensors[device_connected_sensor.unique_internal_name] = device_connected_sensor

        if device.programming.mode is not None:
            device_current_mode_sensor = VoltalisDeviceCurrentModeSensor(entry, device)
            device_sensors[device_current_mode_sensor.unique_internal_name] = device_current_mode_sensor

        # Create the programming sensor for each device (if applicable)
        if device.programming.prog_type is not None:
            device_programming_sensor = VoltalisDeviceProgrammingSensor(entry, device)
            device_sensors[device_programming_sensor.unique_internal_name] = device_programming_sensor

    if not energy_contract_coordinator.data:
        _LOGGER.warning("No Energy contract data available during setup, waiting for first refresh")
        await energy_contract_coordinator.async_config_entry_first_refresh()

    energy_contract_sensors: dict[str, VoltalisEnergyContractEntity] = {}
    for energy_contract in energy_contract_coordinator.data.values():
        contract_subscribed_power_sensor = VoltalisEnergyContractSubscribedPowerSensor(entry, energy_contract)
        energy_contract_sensors[contract_subscribed_power_sensor.unique_internal_name] = (
            contract_subscribed_power_sensor
        )

        contract_current_mode_sensor = VoltalisEnergyContractCurrentModeSensor(entry, energy_contract, date_provider)
        energy_contract_sensors[contract_current_mode_sensor.unique_internal_name] = contract_current_mode_sensor

        contract_kwh_current_cost_sensor = VoltalisEnergyContractKwhCurrentCostSensor(
            entry, energy_contract, date_provider
        )
        energy_contract_sensors[contract_kwh_current_cost_sensor.unique_internal_name] = (
            contract_kwh_current_cost_sensor
        )

        # Create peak/off-peak specific sensors
        if energy_contract.type is VoltalisEnergyContractTypeEnum.PEAK_OFFPEAK:
            contract_kwh_peak_cost_sensor = VoltalisEnergyContractKwhPeakCostSensor(entry, energy_contract)
            energy_contract_sensors[contract_kwh_peak_cost_sensor.unique_internal_name] = contract_kwh_peak_cost_sensor
            contract_kwh_off_peak_cost_sensor = VoltalisEnergyContractKwhOffPeakCostSensor(entry, energy_contract)
            energy_contract_sensors[contract_kwh_off_peak_cost_sensor.unique_internal_name] = (
                contract_kwh_off_peak_cost_sensor
            )

    all_sensors = {**device_sensors, **energy_contract_sensors}
    async_add_entities(all_sensors.values(), update_before_add=True)
    _LOGGER.info(f"Added {len(all_sensors)} Voltalis sensor entities: {list(all_sensors.keys())}")
