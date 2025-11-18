from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature
from homeassistant.exceptions import HomeAssistantError

from custom_components.voltalis.const import (
    VOLTALIS_TO_HA_MODES,
    HA_TO_VOLTALIS_MODES,
    CLIMATE_MIN_TEMP,
    CLIMATE_MAX_TEMP,
    DEFAULT_TARGET_TEMP_STEP,
    CLIMATE_DEFAULT_TEMP,
    CLIMATE_COMFORT_TEMP,
    CLIMATE_BOOST_TEMP_INCREASE,
    DEFAULT_MANUAL_MODE_DURATION,
    DEFAULT_BOOST_DURATION,
    UNTIL_FURTHER_NOTICE_DURATION_DAYS,
)
from custom_components.voltalis.lib.domain.device import (
    VoltalisDevice,
    VoltalisDeviceModeEnum,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity
from custom_components.voltalis.lib.domain.coordinator import VoltalisCoordinator


class VoltalisClimate(VoltalisEntity, ClimateEntity):
    """Climate entity for Voltalis heating devices."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_min_temp = CLIMATE_MIN_TEMP
    _attr_max_temp = CLIMATE_MAX_TEMP
    _attr_target_temperature_step = DEFAULT_TARGET_TEMP_STEP

    def __init__(self, coordinator: VoltalisCoordinator, device: VoltalisDevice) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator, device)
        self._attr_name = None  # Will use device name from device_info
        
        # Build preset modes from available modes
        self._attr_preset_modes = [
            VOLTALIS_TO_HA_MODES[mode]
            for mode in device.available_modes
            if mode in VOLTALIS_TO_HA_MODES
        ]
        
        # Determine supported features
        features = ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF
        
        # Only add temperature control if device supports TEMPERATURE mode
        if VoltalisDeviceModeEnum.TEMPERATURE in device.available_modes:
            features |= ClimateEntityFeature.TARGET_TEMPERATURE
        
        # Add preset mode support if device has available modes
        if self._attr_preset_modes:
            features |= ClimateEntityFeature.PRESET_MODE
        
        self._attr_supported_features = features

    @property
    def _current_device(self) -> VoltalisDevice:
        """Get the current device data from coordinator."""
        data = self.coordinator.data.get(self._device.id)
        return data.device if data else self._device

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        # API doesn't provide current temperature yet
        return None

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        device = self._current_device
        if not device.programming:
            return None
        
        temp = device.programming.temperature_target
        if temp is not None:
            return temp
        
        # Fallback to default temperature if available
        return device.programming.default_temperature

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        device = self._current_device
        if not device.programming or not device.programming.is_on:
            return HVACMode.OFF
        
        # Check programming type to determine mode
        prog_type = device.programming.prog_type
        if prog_type == "MANUAL":
            return HVACMode.HEAT
        
        # DEFAULT or USER planning means AUTO mode
        return HVACMode.AUTO

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return current HVAC action."""
        device = self._current_device
        if not device.programming or not device.programming.is_on:
            return HVACAction.OFF
        
        # If heating_level is present and > 0, device is actively heating
        if device.heating_level is not None and device.heating_level > 0:
            return HVACAction.HEATING
        
        # Device is on but not actively heating
        return HVACAction.IDLE

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        device = self._current_device
        if not device.programming or not device.programming.mode:
            return None
        
        voltalis_mode = device.programming.mode
        return VOLTALIS_TO_HA_MODES.get(voltalis_mode)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
        elif hvac_mode == HVACMode.HEAT:
            # HEAT mode means manual mode with current preset
            await self.__set_manual_mode(is_on=True, use_current_mode=True)
        elif hvac_mode == HVACMode.AUTO:
            # AUTO mode means disable manual mode (use planning)
            await self.__disable_manual_mode()
        else:
            raise HomeAssistantError(f"HVAC mode {hvac_mode} not supported")

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self.__set_manual_mode(is_on=True, use_current_mode=True)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.__set_manual_mode(is_on=False, use_current_mode=True)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        
        # When setting temperature, use TEMPERATURE mode
        await self.__set_manual_mode(
            is_on=True,
            mode=VoltalisDeviceModeEnum.TEMPERATURE,
            temperature=temperature,
        )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        voltalis_mode = HA_TO_VOLTALIS_MODES.get(preset_mode)
        if voltalis_mode is None:
            raise HomeAssistantError(f"Invalid preset mode: {preset_mode}")
        
        await self.__set_manual_mode(is_on=True, mode=voltalis_mode)

    async def __set_manual_mode(
        self,
        is_on: bool,
        use_current_mode: bool = False,
        mode: VoltalisDeviceModeEnum | None = None,
        temperature: float | None = None,
    ) -> None:
        """Set manual mode for the device."""
        device = self._current_device
        
        # Determine the mode to use
        if use_current_mode:
            # Keep current mode or default to ECO
            if device.programming and device.programming.mode:
                target_mode = device.programming.mode
            else:
                target_mode = VoltalisDeviceModeEnum.ECO
        elif mode is not None:
            target_mode = mode
        else:
            target_mode = VoltalisDeviceModeEnum.ECO
        
        # Determine target temperature
        if temperature is not None:
            target_temp = temperature
        elif device.programming and device.programming.temperature_target:
            target_temp = device.programming.temperature_target
        elif device.programming and device.programming.default_temperature:
            target_temp = device.programming.default_temperature
        else:
            target_temp = CLIMATE_DEFAULT_TEMP  # Default fallback
        
        # Set end date to default duration from now
        end_date = (datetime.now() + timedelta(hours=DEFAULT_MANUAL_MODE_DURATION)).isoformat()
        
        # Create manual setting update
        setting = VoltalisManualSettingUpdate(
            enabled=True,  # Enable manual mode
            id_appliance=device.id,
            until_further_notice=False,
            is_on=is_on,
            mode=target_mode,
            end_date=end_date,
            temperature_target=target_temp,
        )
        
        # Get manual setting ID from coordinator data
        data = self.coordinator.data.get(device.id)
        if not data or not data.manual_setting:
            raise HomeAssistantError(f"No manual setting found for device {device.id}")
        
        manual_setting_id = data.manual_setting.id
        
        # Call API to set manual setting
        await self.coordinator.client.set_manual_setting(manual_setting_id, setting)
        
        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    async def __disable_manual_mode(self) -> None:
        """Disable manual mode to return to automatic planning."""
        device = self._current_device
        
        # Get current manual setting or create default
        target_mode = VoltalisDeviceModeEnum.ECO
        target_temp = CLIMATE_DEFAULT_TEMP
        
        if device.programming:
            if device.programming.mode:
                target_mode = device.programming.mode
            if device.programming.temperature_target:
                target_temp = device.programming.temperature_target
            elif device.programming.default_temperature:
                target_temp = device.programming.default_temperature
        
        end_date = datetime.now().isoformat()
        
        # Create manual setting update with enabled=False
        setting = VoltalisManualSettingUpdate(
            enabled=False,  # Disable manual mode
            id_appliance=device.id,
            until_further_notice=False,
            is_on=True,
            mode=target_mode,
            end_date=end_date,
            temperature_target=target_temp,
        )
        
        # Get manual setting ID from coordinator data
        data = self.coordinator.data.get(device.id)
        if not data or not data.manual_setting:
            raise HomeAssistantError(f"No manual setting found for device {device.id}")
        
        manual_setting_id = data.manual_setting.id
        
        # Call API to disable manual setting
        await self.coordinator.client.set_manual_setting(manual_setting_id, setting)
        
        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    def _is_available_from_data(self, data: object) -> bool:
        """Check if entity is available based on device data."""
        if data is None:
            return False
        
        # Climate entity requires device data to be present
        return hasattr(data, "device") and data.device is not None

    # ------------------------------------------------------------------
    # Service action methods
    # ------------------------------------------------------------------
    async def async_service_set_manual_mode(
        self,
        preset_mode: str | None = None,
        temperature: float | None = None,
        duration_hours: int = DEFAULT_MANUAL_MODE_DURATION,
        until_further_notice: bool = False,
    ) -> None:
        """Service action to set manual mode with preset or temperature."""
        device = self._current_device
        
        # Determine the mode to use
        if temperature is not None:
            # Use TEMPERATURE mode if temperature is specified
            target_mode = VoltalisDeviceModeEnum.TEMPERATURE
            target_temp = temperature
        elif preset_mode is not None:
            # Use the specified preset mode
            voltalis_mode = HA_TO_VOLTALIS_MODES.get(preset_mode)
            if voltalis_mode is None:
                raise HomeAssistantError(f"Invalid preset mode: {preset_mode}")
            target_mode = voltalis_mode
            # Use current or default temperature
            if device.programming and device.programming.temperature_target:
                target_temp = device.programming.temperature_target
            elif device.programming and device.programming.default_temperature:
                target_temp = device.programming.default_temperature
            else:
                target_temp = CLIMATE_DEFAULT_TEMP
        else:
            # No mode or temperature specified, use current mode or ECO
            if device.programming and device.programming.mode:
                target_mode = device.programming.mode
            else:
                target_mode = VoltalisDeviceModeEnum.ECO
            
            # Use current or default temperature
            if device.programming and device.programming.temperature_target:
                target_temp = device.programming.temperature_target
            elif device.programming and device.programming.default_temperature:
                target_temp = device.programming.default_temperature
            else:
                target_temp = CLIMATE_DEFAULT_TEMP
        
        # Calculate end date
        if until_further_notice:
            # Set far future date (1 year from now)
            end_date = (datetime.now() + timedelta(days=UNTIL_FURTHER_NOTICE_DURATION_DAYS)).isoformat()
        else:
            end_date = (datetime.now() + timedelta(hours=duration_hours)).isoformat()
        
        # Create manual setting update
        setting = VoltalisManualSettingUpdate(
            enabled=True,
            id_appliance=device.id,
            until_further_notice=until_further_notice,
            is_on=True,
            mode=target_mode,
            end_date=end_date,
            temperature_target=target_temp,
        )
        
        # Get manual setting ID
        data = self.coordinator.data.get(device.id)
        if not data or not data.manual_setting:
            raise HomeAssistantError(f"No manual setting found for device {device.id}")
        
        manual_setting_id = data.manual_setting.id
        
        # Call API
        await self.coordinator.client.set_manual_setting(manual_setting_id, setting)
        
        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    async def async_service_disable_manual_mode(self) -> None:
        """Service action to disable manual mode and return to automatic planning."""
        await self.__disable_manual_mode()

    async def async_service_set_quick_boost(
        self,
        duration_hours: float = DEFAULT_BOOST_DURATION,
        temperature: float | None = None,
    ) -> None:
        """Service action to quickly boost heating for a short period."""
        device = self._current_device
        
        # Determine target temperature and mode
        if temperature is not None:
            target_temp = temperature
            target_mode = VoltalisDeviceModeEnum.TEMPERATURE
        else:
            # Use COMFORT mode for boost
            target_mode = VoltalisDeviceModeEnum.CONFORT
            # Get temperature from device or use default comfort temperature
            if device.programming and device.programming.default_temperature:
                target_temp = device.programming.default_temperature + CLIMATE_BOOST_TEMP_INCREASE  # Boost by configured amount
            else:
                target_temp = CLIMATE_COMFORT_TEMP  # Default comfort temperature
        
        # Calculate end date
        end_date = (datetime.now() + timedelta(hours=duration_hours)).isoformat()
        
        # Create manual setting update
        setting = VoltalisManualSettingUpdate(
            enabled=True,
            id_appliance=device.id,
            until_further_notice=False,
            is_on=True,
            mode=target_mode,
            end_date=end_date,
            temperature_target=target_temp,
        )
        
        # Get manual setting ID
        data = self.coordinator.data.get(device.id)
        if not data or not data.manual_setting:
            raise HomeAssistantError(f"No manual setting found for device {device.id}")
        
        manual_setting_id = data.manual_setting.id
        
        # Call API
        await self.coordinator.client.set_manual_setting(manual_setting_id, setting)
        
        # Refresh coordinator data
        await self.coordinator.async_request_refresh()
