from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

from custom_components.voltalis.apps.home_assistant.coordinators.device import DeviceDto
from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_device_entity import (
    VoltalisDeviceEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.application.devices_management.commands.set_device_temperature_command import (
    SetDeviceTemperatureCommand,
)
from custom_components.voltalis.lib.application.devices_management.commands.turn_off_device_command import (
    TurnOffDeviceCommand,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum


class VoltalisDeviceSwitch(VoltalisDeviceEntity, SwitchEntity):
    """Switch entity for Voltalis heating device on/off state."""

    _attr_translation_key = "device_switch"
    _unique_id_suffix = "device_switch"

    def __init__(self, entry: VoltalisConfigEntry, device: DeviceDto) -> None:
        """Initialize the program select entity."""
        super().__init__(entry, device, entry.runtime_data.voltalis_home_assistant_module.device_coordinator)

        self.__on_mode = (
            DeviceModeEnum.NORMAL if DeviceModeEnum.NORMAL in device.available_modes else DeviceModeEnum.CONFORT
        )

    @property
    def _current_device(self) -> DeviceDto:
        """Get the current device data from coordinator."""
        device = self._voltalis_module.device_coordinator.data.get(self._device.id)
        return device if device else self._device

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        device = self._voltalis_module.device_coordinator.data.get(self._device.id)
        if device is None:
            self._voltalis_module.logger.warning("Device %s not found in coordinator data", self._device.id)
            return

        self._attr_is_on = device.programming.is_on
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        await self.__toggle(is_on=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        await self.__toggle(is_on=False)

    # ------------------------------------------------------------------
    # Internal helper methods
    # ------------------------------------------------------------------

    def __get_appropriate_mode(self, device: DeviceDto, is_on: bool) -> DeviceModeEnum:
        """Determine the appropriate mode based on desired on/off state and device programming."""

        # If turning on, prefer comfort mode if available
        if is_on:
            return self.__on_mode

        # If turning off, keep current mode if possible
        if device.programming.mode and device.programming.mode in device.available_modes:
            return device.programming.mode

        # Fallback to default on mode when turning off (to ensure proper temperature selection)
        return self.__on_mode

    async def __toggle(self, is_on: bool) -> None:
        """Set manual mode for the device.

        When turning on, forces comfort mode for immediate heating.
        When turning off, maintains current mode.
        """
        device = self._current_device

        # Get manual setting ID
        if not device.manual_setting:
            raise HomeAssistantError(f"Manual setting not available for device {device.id}")

        # Determine target mode
        target_mode = self.__get_appropriate_mode(device, is_on)

        if not is_on:
            await self._voltalis_module.turn_off_device_handler.handle(
                TurnOffDeviceCommand(
                    manual_setting_id=device.manual_setting.id,
                    device=device,
                    fallback_mode=target_mode,
                    duration_hours=None,  # Indefinite until user turns it back on
                )
            )
            return

        await self._voltalis_module.set_device_temperature_handler.handle(
            SetDeviceTemperatureCommand(
                manual_setting_id=device.manual_setting.id,
                device=device,
                mode=target_mode,
                duration_hours=None,  # Indefinite until user turns it back off
            )
        )

        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: Device) -> bool:
        return data.programming.is_on is not None
