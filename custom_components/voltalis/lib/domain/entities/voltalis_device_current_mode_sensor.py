from __future__ import annotations

import logging
from enum import StrEnum

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.core import callback

from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinatorData
from custom_components.voltalis.lib.domain.models.device import (
    VoltalisDeviceModeEnum,
)
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceCurrentModeEnum(StrEnum):
    """Voltalis device preset select options."""

    COMFORT = VoltalisDeviceModeEnum.CONFORT.value
    ECO = VoltalisDeviceModeEnum.ECO.value
    FROST_PROTECTION = VoltalisDeviceModeEnum.HORS_GEL.value
    TEMPERATURE = VoltalisDeviceModeEnum.TEMPERATURE.value
    ON = VoltalisDeviceModeEnum.NORMAL.value
    OFF = "off"


class VoltalisDeviceCurrentModeSensor(VoltalisEntity, SensorEntity):
    """Select entity for Voltalis heating device mode."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [option for option in VoltalisDeviceCurrentModeEnum]
    _attr_translation_key = "device_current_mode"
    _unique_id_suffix = "device_current_mode"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data.get(self._device.id)
        if data is None:
            _LOGGER.warning("Device %s not found in coordinator data", self._device.id)
            return
        device = data.device

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

    def _is_available_from_data(self, data: VoltalisCoordinatorData) -> bool:
        return data.device.programming.mode is not None
