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

from custom_components.voltalis.lib.domain.device import (
    VoltalisDevice,
    VoltalisDeviceModeEnum,
    VoltalisManualSettingUpdate,
)
from custom_components.voltalis.lib.domain.voltalis_entity import VoltalisEntity


# Mapping from Voltalis modes to Home Assistant preset modes
PRESET_ECO = "eco"
PRESET_COMFORT = "comfort"
PRESET_FROST_PROTECTION = "frost_protection"
PRESET_NORMAL = "normal"
PRESET_ECOV = "ecov"

VOLTALIS_TO_HA_PRESET = {
    VoltalisDeviceModeEnum.ECO: PRESET_ECO,
    VoltalisDeviceModeEnum.CONFORT: PRESET_COMFORT,
    VoltalisDeviceModeEnum.HORS_GEL: PRESET_FROST_PROTECTION,
    VoltalisDeviceModeEnum.NORMAL: PRESET_NORMAL,
    VoltalisDeviceModeEnum.ECOV: PRESET_ECOV,
}

HA_TO_VOLTALIS_PRESET = {v: k for k, v in VOLTALIS_TO_HA_PRESET.items()}


class VoltalisClimate(VoltalisEntity, ClimateEntity):
    """Climate entity for Voltalis heating devices."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_min_temp = 7.0
    _attr_max_temp = 30.0
    _attr_target_temperature_step = 0.5

    def __init__(self, coordinator, device: VoltalisDevice) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator, device)
        self._attr_name = None  # Will use device name from device_info
        
        # Build preset modes from available modes
        self._attr_preset_modes = [
            VOLTALIS_TO_HA_PRESET[mode]
            for mode in device.available_modes
            if mode in VOLTALIS_TO_HA_PRESET
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
        return VOLTALIS_TO_HA_PRESET.get(voltalis_mode)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
        elif hvac_mode == HVACMode.HEAT:
            # HEAT mode means manual mode with current preset
            await self._set_manual_mode(is_on=True, use_current_mode=True)
        elif hvac_mode == HVACMode.AUTO:
            # AUTO mode means disable manual mode (use planning)
            await self._disable_manual_mode()
        else:
            raise HomeAssistantError(f"HVAC mode {hvac_mode} not supported")

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self._set_manual_mode(is_on=True, use_current_mode=True)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self._set_manual_mode(is_on=False, use_current_mode=True)

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        
        # When setting temperature, use TEMPERATURE mode
        await self._set_manual_mode(
            is_on=True,
            mode=VoltalisDeviceModeEnum.TEMPERATURE,
            temperature=temperature,
        )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        voltalis_mode = HA_TO_VOLTALIS_PRESET.get(preset_mode)
        if voltalis_mode is None:
            raise HomeAssistantError(f"Invalid preset mode: {preset_mode}")
        
        await self._set_manual_mode(is_on=True, mode=voltalis_mode)

    async def _set_manual_mode(
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
            target_temp = 18.0  # Default fallback
        
        # Set end date to 24 hours from now
        end_date = (datetime.now() + timedelta(hours=24)).isoformat()
        
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

    async def _disable_manual_mode(self) -> None:
        """Disable manual mode to return to automatic planning."""
        device = self._current_device
        
        # Get current manual setting or create default
        target_mode = VoltalisDeviceModeEnum.ECO
        target_temp = 18.0
        
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


# Additional sensor entities to avoid frequent state changes in climate entity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature


class VoltalisHeatingLevelSensor(VoltalisEntity, SensorEntity):
    """Sensor for heating level percentage."""

    _attr_device_class = SensorDeviceClass.POWER_FACTOR
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_translation_key = "heating_level"

    def __init__(self, coordinator, device: VoltalisDevice) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_heating_level"
        self._attr_name = "Heating level"

    @property
    def native_value(self) -> int | None:
        """Return the heating level."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.device:
            return data.device.heating_level
        return None


class VoltalisDefaultTemperatureSensor(VoltalisEntity, SensorEntity):
    """Sensor for default temperature setting."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_translation_key = "default_temperature"

    def __init__(self, coordinator, device: VoltalisDevice) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_default_temperature"
        self._attr_name = "Default temperature"

    @property
    def native_value(self) -> float | None:
        """Return the default temperature."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.device and data.device.programming:
            return data.device.programming.default_temperature
        return None


class VoltalisProgrammingTypeSensor(VoltalisEntity, SensorEntity):
    """Sensor for programming type (MANUAL, DEFAULT, USER)."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "programming_type"

    def __init__(self, coordinator, device: VoltalisDevice) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_programming_type"
        self._attr_name = "Programming type"
        self._attr_options = ["MANUAL", "DEFAULT", "USER"]

    @property
    def native_value(self) -> str | None:
        """Return the programming type."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.device and data.device.programming:
            return str(data.device.programming.prog_type)
        return None


class VoltalisProgrammingNameSensor(VoltalisEntity, SensorEntity):
    """Sensor for programming name."""

    _attr_translation_key = "programming_name"

    def __init__(self, coordinator, device: VoltalisDevice) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_programming_name"
        self._attr_name = "Programming name"

    @property
    def native_value(self) -> str | None:
        """Return the programming name."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.device and data.device.programming:
            return data.device.programming.prog_name
        return None


# Import BinarySensorEntity for manual mode sensor
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass


class VoltalisManualModeSensor(VoltalisEntity, BinarySensorEntity):
    """Binary sensor for manual mode status."""

    _attr_device_class = BinarySensorDeviceClass.RUNNING
    _attr_translation_key = "manual_mode"

    def __init__(self, coordinator, device: VoltalisDevice) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_manual_mode"
        self._attr_name = "Manual mode"

    @property
    def is_on(self) -> bool | None:
        """Return true if manual mode is enabled."""
        data = self.coordinator.data.get(self._device.id)
        if data and data.manual_setting:
            return data.manual_setting.enabled
        return None