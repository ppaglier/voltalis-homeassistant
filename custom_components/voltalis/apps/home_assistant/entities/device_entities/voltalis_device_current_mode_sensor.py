from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import callback

from custom_components.voltalis.apps.home_assistant.coordinators.device import DeviceDto
from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_device_entity import (
    VoltalisDeviceEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum


class VoltalisDeviceCurrentModeSensor(VoltalisDeviceEntity, SensorEntity):
    """Select entity for Voltalis heating device mode."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [option for option in DeviceModeEnum]
    _attr_translation_key = "device_current_mode"
    _unique_id_suffix = "device_current_mode"

    def __init__(self, entry: VoltalisConfigEntry, device: DeviceDto) -> None:
        """Initialize the sensor entity."""
        super().__init__(entry, device, entry.runtime_data.voltalis_home_assistant_module.device_coordinator)

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        current = self.native_value
        if current is not None:
            if current == DeviceModeEnum.COMFORT:
                return "mdi:home-thermometer"
            if current == DeviceModeEnum.ECO:
                return "mdi:leaf"
            if current == DeviceModeEnum.AWAY:
                return "mdi:snowflake-alert"
            if current == DeviceModeEnum.TEMPERATURE:
                return "mdi:thermometer"
            if current == DeviceModeEnum.ON:
                return "mdi:flash-outline"
            if current == DeviceModeEnum.OFF:
                return "mdi:power"
        return "mdi:eye-off"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        device = self._voltalis_module.device_coordinator.data.get(self._device.id)
        if device is None:
            self._voltalis_module.logger.warning("Device %s not found in coordinator data", self._device.id)
            return

        # Check if device is off
        self._attr_native_value = DeviceModeEnum.OFF if device.programming.is_on is False else device.programming.mode

        self.async_write_ha_state()

    def _is_available_from_data(self, data: Device) -> bool:
        return data.programming.mode is not None
