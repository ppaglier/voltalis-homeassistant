from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

from custom_components.voltalis.const import (
    CLIMATE_DEFAULT_TEMP,
    HA_TO_VOLTALIS_MODES,
    VOLTALIS_TO_HA_MODES,
    HomeAssistantPresetModeEnum,
)
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.models.device import (
    VoltalisDevice,
    VoltalisDeviceModeEnum,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity

_LOGGER = logging.getLogger(__name__)


class VoltalisProgramSelect(VoltalisEntity, SelectEntity):
    """Select entity for Voltalis heating device program mode."""

    _attr_translation_key = "program_mode"
    _unique_id_suffix = "program_mode"

    def __init__(self, entry: VoltalisConfigEntry, device: VoltalisDevice) -> None:
        """Initialize the program select entity."""
        super().__init__(entry, device)
        self._attr_name = None  # Will use device name from device_info

        # Build options list based on available modes
        options: list[str] = []
        options.append(VoltalisDeviceModeEnum.AUTO)
        for voltalis_mode in device.available_modes:
            program_mode = VOLTALIS_TO_HA_MODES.get(voltalis_mode)
            if program_mode:
                options.append(program_mode)

        # Always add OFF option
        options.append(VoltalisDeviceModeEnum.OFF)


        self._attr_options = options

    @property
    def _current_device(self) -> VoltalisDevice:
        """Get the current device data from coordinator."""
        data = self.coordinator.data.get(self._device.id)
        if data is None:
            return self._device
        return data.device

    @property
    def current_option(self) -> str | None:
        """Return the currently selected program mode."""
        device = self._current_device

        if device.programming is None:
            return HomeAssistantPresetModeEnum.ECO

        # Check if device is off
        if device.programming.is_on is False:
            return VoltalisDeviceModeEnum.OFF

        # Check if device is off
        if  device.programming.id_manual_setting is None:
            return VoltalisDeviceModeEnum.AUTO

        # Get current mode
        if device.programming and device.programming.mode:
            program_mode = VOLTALIS_TO_HA_MODES.get(device.programming.mode)
            if program_mode:
                return program_mode

        # Default to ECO if unknown
        return HomeAssistantPresetModeEnum.ECO

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        current = self.current_option
        if current == VoltalisDeviceModeEnum.CONFORT:
            return "mdi:home-thermometer"
        if current == VoltalisDeviceModeEnum.ECO:
            return "mdi:leaf"
        if current == VoltalisDeviceModeEnum.ECOV:
            return "mdi:leaf-circle"
        if current == VoltalisDeviceModeEnum.HORS_GEL:
            return "mdi:snowflake-alert"
        if current == VoltalisDeviceModeEnum.TEMPERATURE:
            return "mdi:thermometer"
        if current == VoltalisDeviceModeEnum.OFF:
            return "mdi:power"
        if current == VoltalisDeviceModeEnum.AUTO:
            return "mdi:autorenew"
        return "mdi:playlist-edit"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        data = self.coordinator.data.get(self._device.id)
        if data is None:
            _LOGGER.warning("Device %s not found in coordinator data", self._device.id)
            return

        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected program mode."""
        device = self._current_device

        # Handle OFF mode
        if option == VoltalisDeviceModeEnum.OFF:
            await self.__set_manual_mode(is_on=False)
            return
        
        if option == VoltalisDeviceModeEnum.AUTO:
            # Disable manual mode
            await self.__update_manual_settings(
                VoltalisManualSettingUpdate(
                    enabled=False,
                    id_appliance=device.id,
                    until_further_notice=True,
                    is_on=True,
                    mode=None,
                    end_date=None,
                    temperature_target=None,
                )
            )
            return

        # Get Voltalis mode for the selected option
        voltalis_mode = HA_TO_VOLTALIS_MODES.get(option)
        if voltalis_mode is None:
            raise HomeAssistantError(f"Invalid program mode: {option}")

        # Check if mode is available
        if voltalis_mode not in device.available_modes:
            raise HomeAssistantError(f"Mode {option} is not available for this device")

        # Set the mode
        await self.__set_manual_mode(is_on=True, mode=voltalis_mode)

    # ------------------------------------------------------------------
    # Internal helper methods
    # ------------------------------------------------------------------

    async def __update_manual_settings(self, settings: VoltalisManualSettingUpdate) -> None:
        """Update manual settings for the device."""
        device = self._current_device

        # Get manual setting ID
        data = self.coordinator.data.get(device.id)
        if not data or not data.manual_setting:
            raise HomeAssistantError("Manual setting not available for this device")

        manual_setting_id = data.manual_setting.id

        # Call API
        await self.coordinator.client.set_manual_setting(manual_setting_id, settings)

        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    def __get_appropriate_temperature(
        self,
        mode: VoltalisDeviceModeEnum,
        specified_temperature: float | None = None,
    ) -> float:
        """Determine the appropriate temperature based on mode and device programming."""
        device = self._current_device

        if specified_temperature is not None:
            return specified_temperature

        # Use device programming temperature if available
        if device.programming and device.programming.temperature_target:
            return device.programming.temperature_target

        # Use default temperature from device programming
        if device.programming and device.programming.default_temperature:
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
        elif device.programming and device.programming.mode:
            target_mode = device.programming.mode

        # Determine target temperature
        target_temp = self.__get_appropriate_temperature(target_mode)

        await self.__update_manual_settings(
            VoltalisManualSettingUpdate(
                enabled=True,
                id_appliance=device.id,
                until_further_notice=True,
                is_on=is_on,
                mode=target_mode,
                end_date=None,
                temperature_target=target_temp,
            )
        )

    def _is_available_from_data(self, data: object) -> bool:
        """Check if entity is available based on device data."""
        if data is None:
            return False

        # Program select requires device data to be present
        return hasattr(data, "device") and data.device is not None
