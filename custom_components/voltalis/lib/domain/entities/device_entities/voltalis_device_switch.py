from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

from custom_components.voltalis.const import CLIMATE_COMFORT_TEMP, CLIMATE_DEFAULT_TEMP
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinators.device import VoltalisDeviceCoordinatorData
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_device_entity import VoltalisDeviceEntity
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceModeEnum
from custom_components.voltalis.lib.domain.models.manual_setting import VoltalisManualSettingUpdate

_LOGGER = logging.getLogger(__name__)


class VoltalisDeviceSwitch(VoltalisDeviceEntity, SwitchEntity):
    """Switch entity for Voltalis heating device on/off state."""

    _attr_translation_key = "device_switch"
    _unique_id_suffix = "device_switch"

    def __init__(self, entry: VoltalisConfigEntry, device: VoltalisDeviceCoordinatorData) -> None:
        """Initialize the program select entity."""
        super().__init__(entry, device, entry.runtime_data.coordinators.device)

    @property
    def _current_device(self) -> VoltalisDeviceCoordinatorData:
        """Get the current device data from coordinator."""
        device = self._coordinators.device.data.get(self._device.id)
        return device if device else self._device

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        device = self._coordinators.device.data.get(self._device.id)
        if device is None:
            _LOGGER.warning("Device %s not found in coordinator data", self._device.id)
            return

        self._attr_is_on = device.programming.is_on
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self.__set_manual_mode(is_on=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.__set_manual_mode(is_on=False)

    # ------------------------------------------------------------------
    # Internal helper methods
    # ------------------------------------------------------------------

    async def __update_manual_settings(self, settings: VoltalisManualSettingUpdate) -> None:
        """Update manual settings for the device."""
        device = self._current_device

        # Get manual setting ID
        if not device.manual_setting:
            raise HomeAssistantError(f"Manual setting not available for device {device.id}")

        manual_setting_id = device.manual_setting.id

        # Call API
        await self._coordinators.device.set_manual_setting(manual_setting_id, settings)

        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    def __get_appropriate_temperature(
        self,
        mode: VoltalisDeviceModeEnum,
        specified_temperature: float | None = None,
    ) -> float:
        """Determine the appropriate temperature based on mode and device programming."""

        if specified_temperature is not None:
            return specified_temperature

        device = self._current_device

        # Use device programming temperature if available
        if device.programming.temperature_target:
            return device.programming.temperature_target

        # Use default temperature from device programming
        if device.programming.default_temperature:
            return device.programming.default_temperature

        # Fallbacks based on mode
        if mode == VoltalisDeviceModeEnum.CONFORT:
            return CLIMATE_COMFORT_TEMP

        # Fallback to constant
        return CLIMATE_DEFAULT_TEMP

    async def __set_manual_mode(self, is_on: bool) -> None:
        """Set manual mode for the device."""
        device = self._current_device

        # Determine the mode to use
        target_mode = VoltalisDeviceModeEnum.ECO
        if device.programming.mode:
            # Keep current mode
            target_mode = device.programming.mode

        # Determine target temperature
        target_temp = self.__get_appropriate_temperature(target_mode)

        await self.__update_manual_settings(
            VoltalisManualSettingUpdate(
                enabled=True,  # Enable manual mode
                id_appliance=device.id,
                until_further_notice=True,
                is_on=is_on,
                mode=target_mode,
                end_date=None,
                temperature_target=target_temp,
            )
        )

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: VoltalisDevice) -> bool:
        return data.programming.is_on is not None
