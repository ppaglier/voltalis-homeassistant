from typing import Literal

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.const import UnitOfEnergy
from homeassistant.core import callback

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_device_entity import (
    VoltalisDeviceEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto


class VoltalisDeviceEnergyDailySensor(VoltalisDeviceEntity, SensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """References the daily energy of a device."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = None
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        device: DeviceDto,
        sensor_type: Literal["peak", "off-peak"] | None,
    ) -> None:
        """Initialize the sensor entity."""

        suffix = f"_{sensor_type}" if sensor_type else ""
        self.__sensor_type = sensor_type
        self._attr_translation_key = f"device_energy_daily{suffix}"

        super().__init__(
            entry, device, entry.runtime_data.voltalis_home_assistant_module.device_energy_daily_coordinator
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        data = self._voltalis_module.device_energy_daily_coordinator.data.get(self._device.id)
        if data is None:
            self._voltalis_module.logger.warning(
                "Daily energy %s data for device %s is None", self.__sensor_type, self._device.id
            )
            return

        new_value = sum(
            [
                (
                    record.total
                    if self.__sensor_type is None
                    else (record.peak or 0.0)
                    if self.__sensor_type == "peak"
                    else (record.off_peak or 0.0)
                )
                for record in data.daily_energy_records
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
