from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature

from custom_components.voltalis.lib.domain.device import (
    VoltalisDevice,
    VoltalisDeviceModeEnum,
    VoltalisDeviceTypeEnum,
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
        # TODO: Implement via API when available
        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()
        elif hvac_mode in (HVACMode.HEAT, HVACMode.AUTO):
            await self.async_turn_on()
        else:
            raise NotImplementedError(f"HVAC mode {hvac_mode} not supported")

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        # TODO: Implement via API when available
        raise NotImplementedError("Turn on not yet implemented - API support required")

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        # TODO: Implement via API when available
        raise NotImplementedError("Turn off not yet implemented - API support required")

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        # TODO: Implement via API when available
        temperature = kwargs.get("temperature")
        if temperature is None:
            return
        
        raise NotImplementedError("Set temperature not yet implemented - API support required")

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        # TODO: Implement via API when available
        voltalis_mode = HA_TO_VOLTALIS_PRESET.get(preset_mode)
        if voltalis_mode is None:
            raise ValueError(f"Invalid preset mode: {preset_mode}")
        
        raise NotImplementedError("Set preset mode not yet implemented - API support required")

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