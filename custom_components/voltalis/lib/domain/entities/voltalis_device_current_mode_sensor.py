from __future__ import annotations

import logging
from enum import StrEnum

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceModeEnum
from custom_components.voltalis.lib.domain.voltalis_device_entity import VoltalisDeviceEntity

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceCurrentModeEnum(StrEnum):
    """Voltalis device preset select options."""

    COMFORT = VoltalisDeviceModeEnum.CONFORT.value
    ECO = VoltalisDeviceModeEnum.ECO.value
    FROST_PROTECTION = VoltalisDeviceModeEnum.HORS_GEL.value
    TEMPERATURE = VoltalisDeviceModeEnum.TEMPERATURE.value
    ON = VoltalisDeviceModeEnum.NORMAL.value
    OFF = "off"


class VoltalisDeviceCurrentModeSensor(VoltalisDeviceEntity, SensorEntity):
    """Select entity for Voltalis heating device mode."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [option for option in VoltalisDeviceCurrentModeEnum]
    _attr_translation_key = "device_current_mode"
    _unique_id_suffix = "device_current_mode"

    def __init__(self, entry: VoltalisConfigEntry, device: VoltalisDevice) -> None:
        """Initialize the sensor entity."""
        super().__init__(entry, device, entry.runtime_data.coordinators.device)

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        current = self.native_value
        if current is not None:
            if current == VoltalisDeviceCurrentModeEnum.COMFORT:
                return "mdi:home-thermometer"
            if current == VoltalisDeviceCurrentModeEnum.ECO:
                return "mdi:leaf"
            if current == VoltalisDeviceCurrentModeEnum.FROST_PROTECTION:
                return "mdi:snowflake-alert"
            if current == VoltalisDeviceCurrentModeEnum.TEMPERATURE:
                return "mdi:thermometer"
            if current == VoltalisDeviceCurrentModeEnum.ON:
                return "mdi:flash-outline"
            if current == VoltalisDeviceCurrentModeEnum.OFF:
                return "mdi:power"
        return "mdi:eye-off"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        device = self._coordinators.device.data.get(self._device.id)
        if device is None:
            _LOGGER.warning("Device %s not found in coordinator data", self._device.id)
            return

        def get_current_option() -> str | None:
            # Check if device is off
            if device.programming.is_on is False:
                return VoltalisDeviceCurrentModeEnum.OFF

            # Get current mode
            current_mode = device.programming.mode
            # Handle ECOV mode
            if current_mode == VoltalisDeviceModeEnum.ECOV:
                return VoltalisDeviceCurrentModeEnum.ECO
            return current_mode

        self._attr_native_value = get_current_option()
        self.async_write_ha_state()

    def _is_available_from_data(self, data: VoltalisDevice) -> bool:
        return data.programming.mode is not None
