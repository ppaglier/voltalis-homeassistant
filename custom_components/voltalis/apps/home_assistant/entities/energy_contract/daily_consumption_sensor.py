from typing import Literal

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.const import UnitOfEnergy
from propcache.api import cached_property

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_energy_contract_entity import (
    VoltalisEnergyContractEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract


class VoltalisEnergyContractDailyConsumptionSensor(VoltalisEnergyContractEntity, SensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """Sensor entity to represent near real-time consumption for a Voltalis energy contract."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = None
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        energy_contract: EnergyContract,
        sensor_type: Literal["peak", "offpeak"] | None,
    ) -> None:
        """Initialize the sensor entity."""

        self._attr_translation_key = "daily_consumption_" + sensor_type if sensor_type else "daily_consumption"
        self._unique_id_suffix = "daily_consumption_" + sensor_type if sensor_type else "daily_consumption"
        statistic_suffix = f"_{sensor_type}" if sensor_type else ""
        self._statistic_id = f"voltalis:contract_{entry.entry_id.lower()}_{energy_contract.id}_energy{statistic_suffix}"
        super().__init__(
            entry,
            energy_contract,
            entry.runtime_data.voltalis_home_assistant_module.device_daily_consumption_coordinator,
        )

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self._register_statistics_updates()

    async def async_will_remove_from_hass(self) -> None:
        self._unregister_statistics_updates()
        await super().async_will_remove_from_hass()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    @cached_property
    def available(self) -> bool:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Return if the entity is available."""
        if not self.coordinator.data:
            return False
        return self.coordinator.last_update_success

    def _is_available_from_data(self, data: float) -> bool:
        return True
