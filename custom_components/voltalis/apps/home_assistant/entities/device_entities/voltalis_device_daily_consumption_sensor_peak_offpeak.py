from typing import Literal

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.const import UnitOfEnergy

from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_device_entity import (
    VoltalisDeviceEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.application.devices_management.dtos.device_dto import DeviceDto


class VoltalisDeviceDailyConsumptionPeakOffPeakSensor(VoltalisDeviceEntity, SensorEntity):  # pyright: ignore[reportIncompatibleVariableOverride]
    """References the daily consumption of a device, for peak and off-peak periods."""

    _attr_device_class = SensorDeviceClass.ENERGY
    _attr_state_class = None
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR

    def __init__(
        self,
        entry: VoltalisConfigEntry,
        device: DeviceDto,
        sensor_type: Literal["peak", "offpeak"],
    ) -> None:
        """Initialize the sensor entity."""
        self._statistic_id = f"voltalis:device_{entry.entry_id.lower()}_{device.id}_energy_{sensor_type}"
        self._attr_translation_key = "device_daily_consumption_" + sensor_type
        self._unique_id_suffix = "device_daily_consumption_" + sensor_type

        super().__init__(
            entry, device, entry.runtime_data.voltalis_home_assistant_module.device_daily_consumption_coordinator
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
    def _is_available_from_data(self, data: float) -> bool:
        return True
