from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_base_entity import (
    VoltalisBaseEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_device_entity import (
    VoltalisDeviceEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.apps.home_assistant.entities.device_entities.voltalis_device_connected_sensor import (
    VoltalisDeviceConnectedSensor,
)
from custom_components.voltalis.apps.home_assistant.entities.device_entities.voltalis_device_current_mode_sensor import (  # noqa: E501
    VoltalisDeviceCurrentModeSensor,
)
from custom_components.voltalis.apps.home_assistant.entities.device_entities.voltalis_device_daily_consumption_sensor import (  # noqa: E501
    VoltalisDeviceDailyConsumptionSensor,
)
from custom_components.voltalis.apps.home_assistant.entities.device_entities.voltalis_device_programming_sensor import (
    VoltalisDeviceProgrammingSensor,
)
from custom_components.voltalis.apps.home_assistant.entities.energy_contract.current_tariff_sensor import (
    VoltalisEnergyContractCurrentTariffSensor,
)
from custom_components.voltalis.apps.home_assistant.entities.energy_contract.daily_consumption_sensor import (
    VoltalisEnergyContractDailyConsumptionSensor,
)
from custom_components.voltalis.apps.home_assistant.entities.energy_contract.kwh_current_price_sensor import (
    VoltalisEnergyContractKwhCurrentPriceSensor,
)
from custom_components.voltalis.apps.home_assistant.entities.energy_contract.kwh_price_sensor import (
    VoltalisEnergyContractKwhPriceSensor,
)
from custom_components.voltalis.apps.home_assistant.entities.energy_contract.live_power_sensor import (
    VoltalisEnergyContractLivePowerSensor,
)
from custom_components.voltalis.apps.home_assistant.entities.energy_contract.subscribed_power_sensor import (
    VoltalisEnergyContractSubscribedPowerSensor,
)
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract_enum import EnergyContractTypeEnum

# Limit parallel updates (the DataUpdateCoordinator already centralizes calls)
PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: VoltalisConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Voltalis sensors from a config entry."""

    voltalis_home_assistant_module = entry.runtime_data.voltalis_home_assistant_module
    device_coordinator = voltalis_home_assistant_module.device_coordinator
    health_coordinator = voltalis_home_assistant_module.device_health_coordinator
    energy_contract_coordinator = voltalis_home_assistant_module.energy_contract_coordinator

    energy_contract_sensors: list[VoltalisEnergyContractEntity] = []
    current_contract = next(iter(energy_contract_coordinator.data.values()), None)
    if current_contract is not None:
        energy_contract_sensors.append(VoltalisEnergyContractLivePowerSensor(entry, current_contract))
        energy_contract_sensors.append(VoltalisEnergyContractSubscribedPowerSensor(entry, current_contract))

        energy_contract_sensors.append(VoltalisEnergyContractDailyConsumptionSensor(entry, current_contract, None))

        # Create peak/off-peak specific sensors
        if current_contract.type == EnergyContractTypeEnum.BASE:
            energy_contract_sensors.append(VoltalisEnergyContractKwhPriceSensor(entry, current_contract, None))

        elif current_contract.type == EnergyContractTypeEnum.PEAK_OFF_PEAK:
            energy_contract_sensors.append(VoltalisEnergyContractCurrentTariffSensor(entry, current_contract))
            energy_contract_sensors.append(VoltalisEnergyContractKwhCurrentPriceSensor(entry, current_contract))
            energy_contract_sensors.append(VoltalisEnergyContractKwhPriceSensor(entry, current_contract, "peak"))
            energy_contract_sensors.append(VoltalisEnergyContractKwhPriceSensor(entry, current_contract, "off-peak"))

            energy_contract_sensors.append(
                VoltalisEnergyContractDailyConsumptionSensor(entry, current_contract, "peak")
            )
            energy_contract_sensors.append(
                VoltalisEnergyContractDailyConsumptionSensor(entry, current_contract, "off-peak")
            )

    device_sensors: list[VoltalisDeviceEntity] = []

    for device in device_coordinator.data.values():
        # Create the consumption sensor for each device
        device_sensors.append(VoltalisDeviceDailyConsumptionSensor(entry, device, None))

        # Create the connected sensor for each device (if status is available)
        if health_coordinator.data.get(device.id) is not None:
            device_sensors.append(VoltalisDeviceConnectedSensor(entry, device))

        if device.programming.mode is not None:
            device_sensors.append(VoltalisDeviceCurrentModeSensor(entry, device))

        # Create the programming sensor for each device (if applicable)
        if device.programming.prog_type is not None:
            device_sensors.append(VoltalisDeviceProgrammingSensor(entry, device))

        if current_contract is not None and (current_contract.type == EnergyContractTypeEnum.PEAK_OFF_PEAK):
            device_sensors.append(VoltalisDeviceDailyConsumptionSensor(entry, device, "peak"))
            device_sensors.append(VoltalisDeviceDailyConsumptionSensor(entry, device, "off-peak"))

    all_entities: dict[str, VoltalisBaseEntity] = {
        sensor.unique_internal_name: sensor for sensor in (energy_contract_sensors + device_sensors)
    }
    async_add_entities(all_entities.values(), update_before_add=True)
    voltalis_home_assistant_module.logger.info(
        f"Added {len(all_entities)} Voltalis sensor entities: {list(all_entities.keys())}"
    )
