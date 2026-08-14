from typing import Literal

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfEnergy
from homeassistant.core import callback

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_device_entity import (
    VoltalisDeviceEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto
from custom_components.voltalis.lib.domain.energy_contracts.energy_contract import EnergyContract
from custom_components.voltalis.lib.domain.helpers.is_in_time_range import is_in_time_range


class VoltalisDeviceDailyConsumptionPeakOffPeakSensor(VoltalisDeviceEntity, SensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """References the daily consumption of a device, for peak and off-peak periods."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        device: DeviceDto,
        energy_contract: EnergyContract,
        sensor_type: Literal["peak", "offpeak"],
    ) -> None:
        """Initialize the sensor entity."""
        self._attr_translation_key = "device_daily_consumption_" + sensor_type
        self._unique_id_suffix = "device_daily_consumption_" + sensor_type

        self._attr_icon = "mdi:transmission-tower"

        super().__init__(
            entry, device, entry.runtime_data.voltalis_home_assistant_module.device_daily_consumption_coordinator
        )

        self.__sensor_type = sensor_type
        self.__sensor_type_hours = (
            energy_contract.peak_hours if sensor_type == "peak" else energy_contract.offpeak_hours
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        data = self._voltalis_module.device_daily_consumption_coordinator.data.get(self._device.id)
        if data is None:
            self._voltalis_module.logger.warning(
                "Daily consumption %s data for device %s is None", self.__sensor_type, self._device.id
            )
            return

        new_value = sum(
            [
                consumption
                for (time, consumption) in data.daily_consumption_records
                if any(is_in_time_range(time_range, time) for time_range in self.__sensor_type_hours)
            ],
            0.0,
        )
        if self.native_value == new_value:
            return

        self._attr_native_value = new_value
        self.async_write_ha_state()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: float) -> bool:
        return True
