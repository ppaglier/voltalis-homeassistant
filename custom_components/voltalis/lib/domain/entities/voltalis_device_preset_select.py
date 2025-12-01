from __future__ import annotations

import logging
from enum import StrEnum
from typing import cast

from homeassistant.components.select import SelectEntity
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

from custom_components.voltalis.const import CLIMATE_DEFAULT_TEMP
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinators.device import VoltalisDeviceCoordinatorData
from custom_components.voltalis.lib.domain.models.device import VoltalisDevice, VoltalisDeviceModeEnum
from custom_components.voltalis.lib.domain.models.manual_setting import VoltalisManualSettingUpdate
from custom_components.voltalis.lib.domain.voltalis_device_entity import VoltalisDeviceEntity

_LOGGER = logging.getLogger(__name__)


class VoltalisDevicePresetSelectOptionsEnum(StrEnum):
    """Voltalis device preset select options."""

    COMFORT = VoltalisDeviceModeEnum.CONFORT.value
    ECO = VoltalisDeviceModeEnum.ECO.value
    FROST_PROTECTION = VoltalisDeviceModeEnum.HORS_GEL.value
    TEMPERATURE = VoltalisDeviceModeEnum.TEMPERATURE.value
    ON = VoltalisDeviceModeEnum.NORMAL.value
    OFF = "off"
    AUTO = "auto"


class VoltalisDevicePresetSelect(VoltalisDeviceEntity, SelectEntity):
    """Select entity for Voltalis heating device mode."""

    _attr_translation_key = "device_preset"
    _unique_id_suffix = "device_preset"

    def __init__(self, entry: VoltalisConfigEntry, device: VoltalisDeviceCoordinatorData) -> None:
        """Initialize the program select entity."""
        super().__init__(entry, device, entry.runtime_data.coordinators.device)

        self.__has_ecov_mode = VoltalisDeviceModeEnum.ECOV in device.available_modes
        self.__has_on_mode = VoltalisDeviceModeEnum.NORMAL in device.available_modes

        # Build options modes from available modes
        options: list[str] = []
        for voltalis_mode in VoltalisDevicePresetSelectOptionsEnum:
            # Skip AUTO | ON | NONE mode here, will add it after the loop
            if voltalis_mode in [
                VoltalisDevicePresetSelectOptionsEnum.AUTO,
                VoltalisDevicePresetSelectOptionsEnum.ON,
                VoltalisDevicePresetSelectOptionsEnum.OFF,
            ]:
                continue

            if voltalis_mode not in device.available_modes:
                # Special handling for ECOV mode
                if (
                    self.__has_ecov_mode and voltalis_mode != VoltalisDevicePresetSelectOptionsEnum.ECO
                ) or not self.__has_ecov_mode:
                    continue
                voltalis_mode = VoltalisDevicePresetSelectOptionsEnum.ECO

            if voltalis_mode not in options:
                options.append(voltalis_mode)

        self._attr_options = (
            [VoltalisDevicePresetSelectOptionsEnum.AUTO]
            + ([VoltalisDevicePresetSelectOptionsEnum.ON] if self.__has_on_mode else [])
            + options
            + [VoltalisDevicePresetSelectOptionsEnum.OFF]
        )

    @property
    def _current_device(self) -> VoltalisDeviceCoordinatorData:
        """Get the current device data from coordinator."""
        device = self._coordinators.device.data.get(self._device.id)
        return device if device else self._device

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        current = self.current_option
        if current is not None:
            if current == VoltalisDevicePresetSelectOptionsEnum.COMFORT:
                return "mdi:home-thermometer"
            if current == VoltalisDevicePresetSelectOptionsEnum.ECO:
                return "mdi:leaf"
            if current == VoltalisDevicePresetSelectOptionsEnum.FROST_PROTECTION:
                return "mdi:snowflake-alert"
            if current == VoltalisDevicePresetSelectOptionsEnum.TEMPERATURE:
                return "mdi:thermometer"
            if current == VoltalisDevicePresetSelectOptionsEnum.ON:
                return "mdi:flash-outline"
            if current == VoltalisDevicePresetSelectOptionsEnum.OFF:
                return "mdi:power"
            if current == VoltalisDevicePresetSelectOptionsEnum.AUTO:
                return "mdi:autorenew"
        return "mdi:playlist-edit"

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
                return VoltalisDevicePresetSelectOptionsEnum.OFF

            # Check if device is off
            if device.programming.id_manual_setting is None:
                return VoltalisDevicePresetSelectOptionsEnum.AUTO

            # Get current mode
            current_mode = device.programming.mode
            # Handle ECOV mode
            if current_mode == VoltalisDeviceModeEnum.ECOV:
                return VoltalisDevicePresetSelectOptionsEnum.ECO
            return current_mode

        self._attr_current_option = get_current_option()
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected program mode."""

        # Handle OFF mode
        if option == VoltalisDevicePresetSelectOptionsEnum.OFF:
            await self.__set_manual_mode(is_on=False, mode=VoltalisDeviceModeEnum.NORMAL)
            return

        # Disable manual mode
        if option == VoltalisDevicePresetSelectOptionsEnum.AUTO:
            await self.__set_manual_mode(is_on=True, mode=None)
            return

        # Handle ECOV mode
        if option == VoltalisDeviceModeEnum.ECO and self.__has_ecov_mode:
            option = VoltalisDeviceModeEnum.ECOV

        # Set the mode
        await self.__set_manual_mode(is_on=True, mode=cast(VoltalisDeviceModeEnum, option))

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
        specified_temperature: float | None = None,
    ) -> float:
        """Determine the appropriate temperature based on mode and device programming."""
        device = self._current_device

        if specified_temperature is not None:
            return specified_temperature

        # Use device programming temperature if available
        if device.programming.temperature_target:
            return device.programming.temperature_target

        # Use default temperature from device programming
        if device.programming.default_temperature:
            return device.programming.default_temperature

        # Fallback to constant
        return CLIMATE_DEFAULT_TEMP

    async def __set_manual_mode(
        self,
        is_on: bool,
        mode: VoltalisDeviceModeEnum | None = None,
    ) -> None:
        """Set manual mode for the device."""
        device = self._current_device

        # Determine the mode to use
        target_mode = VoltalisDeviceModeEnum.ECO
        if mode is not None:
            target_mode = mode
        elif device.programming.mode:
            # Keep current mode
            target_mode = device.programming.mode

        # Determine target temperature
        target_temp = self.__get_appropriate_temperature()

        await self.__update_manual_settings(
            VoltalisManualSettingUpdate(
                enabled=mode is not None,
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
        return data.programming.is_on is not None and data.programming.mode is not None
