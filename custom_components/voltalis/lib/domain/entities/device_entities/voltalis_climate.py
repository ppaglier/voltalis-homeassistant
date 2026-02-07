from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, cast

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACAction, HVACMode
from homeassistant.exceptions import HomeAssistantError

from custom_components.voltalis.const import (
    CLIMATE_BOOST_DURATION,
    CLIMATE_BOOST_TEMP_INCREASE,
    CLIMATE_COMFORT_TEMP,
    CLIMATE_DEFAULT_TEMP,
    CLIMATE_MAX_TEMP,
    CLIMATE_MIN_TEMP,
    CLIMATE_TEMP_STEP,
    CLIMATE_UNIT,
    HA_TO_VOLTALIS_MODES,
    VOLTALIS_TO_HA_MODES,
    HomeAssistantPresetModeEnum,
)
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinators.device import VoltalisDeviceCoordinatorData
from custom_components.voltalis.lib.domain.entities.base_entities.voltalis_device_entity import VoltalisDeviceEntity
from custom_components.voltalis.lib.domain.models.device import (
    VoltalisDevice,
    VoltalisDeviceModeEnum,
    VoltalisDeviceProgTypeEnum,
)
from custom_components.voltalis.lib.domain.models.manual_setting import VoltalisManualSettingUpdate


class VoltalisClimate(VoltalisDeviceEntity, ClimateEntity):
    """Climate entity for Voltalis heating devices."""

    _attr_temperature_unit = CLIMATE_UNIT
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_min_temp = CLIMATE_MIN_TEMP
    _attr_max_temp = CLIMATE_MAX_TEMP
    _attr_target_temperature_step = CLIMATE_TEMP_STEP
    _unique_id_suffix = "climate"

    def __init__(self, entry: VoltalisConfigEntry, device: VoltalisDeviceCoordinatorData) -> None:
        """Initialize the climate entity."""
        super().__init__(entry, device, entry.runtime_data.coordinators.device)
        # We don't set name there because this is only one entity per device
        # and the device name is already used for the main entity.
        self._attr_name = None

        # Build preset modes from available modes
        presets: list[str] = []
        for voltalis_mode in VOLTALIS_TO_HA_MODES:
            ha_mode = VOLTALIS_TO_HA_MODES[voltalis_mode]
            # Skip NONE mode here, will add it at the end
            if ha_mode is HomeAssistantPresetModeEnum.NONE:
                continue
            if voltalis_mode in device.available_modes and ha_mode not in presets:
                presets.append(ha_mode)

        self._attr_preset_modes = presets + [HomeAssistantPresetModeEnum.NONE]

        # Determine supported features
        features = ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF

        # Add preset mode support if device has available modes other than HomeAssistantPresetModeEnum.NONE
        if len(self._attr_preset_modes) > 1:
            features |= ClimateEntityFeature.PRESET_MODE

        # Only add temperature control if device supports TEMPERATURE mode
        if VoltalisDeviceModeEnum.TEMPERATURE in self._device.available_modes:
            features |= ClimateEntityFeature.TARGET_TEMPERATURE

        self._attr_supported_features = features

    @property
    def _current_device(self) -> VoltalisDeviceCoordinatorData:
        """Get the current device data from coordinator."""
        device = self._coordinators.device.data.get(self._device.id)
        return device if device else self._device

    # ------------------------------------------------------------------
    # Temperature handling
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # HVAC mode handling
    # ------------------------------------------------------------------

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        device = self._current_device
        if not device.programming or not device.programming.is_on:
            return HVACMode.OFF

        # Check programming type to determine mode
        prog_type = device.programming.prog_type
        if prog_type == VoltalisDeviceProgTypeEnum.MANUAL:
            return HVACMode.HEAT

        # DEFAULT or USER planning means AUTO mode
        return HVACMode.AUTO

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return current HVAC action."""
        device = self._current_device

        # Determine action based on programming status
        if device.programming.is_on:
            # Device is on but not actively heating
            if device.programming.mode == VoltalisDeviceModeEnum.HORS_GEL:
                return HVACAction.IDLE
            return HVACAction.HEATING
        return HVACAction.OFF

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""

        if hvac_mode == HVACMode.OFF:
            await self.async_turn_off()  # Turn off device
        elif hvac_mode == HVACMode.HEAT:
            await self.__set_manual_mode(is_on=True)  # Use current mode
        elif hvac_mode == HVACMode.AUTO:
            await self.__disable_manual_mode()  # Return to automatic programming
        else:
            raise HomeAssistantError(f"HVAC mode {hvac_mode} not supported")

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        await self.__set_manual_mode(is_on=True)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        await self.__set_manual_mode(is_on=False)

    # ------------------------------------------------------------------
    # Preset mode handling
    # ------------------------------------------------------------------

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        device = self._current_device
        if not device.programming or not device.programming.mode:
            return None

        voltalis_mode = device.programming.mode
        return VOLTALIS_TO_HA_MODES.get(voltalis_mode)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        voltalis_mode = HA_TO_VOLTALIS_MODES.get(cast(HomeAssistantPresetModeEnum, preset_mode))
        if voltalis_mode is None:
            raise HomeAssistantError(f"Invalid preset mode: {preset_mode}")

        await self.__set_manual_mode(is_on=True, mode=voltalis_mode)

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
        """Determine the appropriate temperature based on mode and specified temperature."""
        device = self._current_device

        if specified_temperature is not None:
            return specified_temperature

        # Use device programming or defaults
        # TODO : Test de l'importance de la température envoyée dans les modes autres que TEMPERATURE
        # TODO : Sinon établir un tableau de températures par défaut / voir demandé à l'utilisateur pendant la config
        if device.programming:
            if device.programming.temperature_target is not None:
                return device.programming.temperature_target
            if device.programming.default_temperature is not None:
                return device.programming.default_temperature

        # Fallbacks based on mode
        if mode == VoltalisDeviceModeEnum.CONFORT:
            return CLIMATE_COMFORT_TEMP

        return CLIMATE_DEFAULT_TEMP

    async def __set_manual_mode(
        self,
        is_on: bool,
        mode: VoltalisDeviceModeEnum | None = None,
        temperature: float | None = None,
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
        target_temp = self.__get_appropriate_temperature(target_mode, temperature)

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

        await self.__update_manual_settings(
            VoltalisManualSettingUpdate(
                enabled=False,  # Disable manual mode
                id_appliance=device.id,
                until_further_notice=False,
                is_on=True,
                mode=target_mode,
                end_date=end_date,
                temperature_target=target_temp,
            )
        )

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: VoltalisDevice) -> bool:
        return data.programming.is_on is not None and data.programming.mode is not None

    # ------------------------------------------------------------------
    # Service action methods
    # ------------------------------------------------------------------
    async def async_service_set_manual_mode(
        self,
        preset_mode: str | None = None,
        temperature: float | None = None,
        duration_hours: int | None = None,
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
            voltalis_mode = HA_TO_VOLTALIS_MODES.get(cast(HomeAssistantPresetModeEnum, preset_mode))
            if voltalis_mode is None:
                raise HomeAssistantError(f"Invalid preset mode: {preset_mode}")
            target_mode = voltalis_mode
            # Use current or default temperature
            target_temp = self.__get_appropriate_temperature(target_mode)
        else:
            # No mode or temperature specified, use current mode or ECO
            if device.programming.mode:
                target_mode = device.programming.mode
            else:
                target_mode = VoltalisDeviceModeEnum.ECO

            # Use current or default temperature
            target_temp = self.__get_appropriate_temperature(target_mode)

        # Calculate end date
        end_date = None if duration_hours is None else (datetime.now() + timedelta(hours=duration_hours)).isoformat()

        await self.__update_manual_settings(
            VoltalisManualSettingUpdate(
                enabled=True,
                id_appliance=device.id,
                until_further_notice=duration_hours is None,
                is_on=True,
                mode=target_mode,
                end_date=end_date,
                temperature_target=target_temp,
            )
        )

    async def async_service_disable_manual_mode(self) -> None:
        """Service action to disable manual mode and return to automatic planning."""
        await self.__disable_manual_mode()

    async def async_service_set_quick_boost(
        self,
        duration_hours: float = CLIMATE_BOOST_DURATION,
        temperature: float | None = None,
    ) -> None:
        """Service action to quickly boost heating for a short period."""
        device = self._current_device

        # Determine target temperature and mode
        target_temp = temperature
        target_mode = VoltalisDeviceModeEnum.TEMPERATURE
        if target_temp is None:
            # Use COMFORT mode for boost
            target_mode = VoltalisDeviceModeEnum.CONFORT
            target_temp = CLIMATE_COMFORT_TEMP
            # Get temperature from device or use default comfort temperature
            if device.programming.default_temperature:
                target_temp = (
                    device.programming.default_temperature + CLIMATE_BOOST_TEMP_INCREASE
                )  # Boost by configured amount

        # Calculate end date
        end_date = (datetime.now() + timedelta(hours=duration_hours)).isoformat()

        await self.__update_manual_settings(
            VoltalisManualSettingUpdate(
                enabled=True,
                id_appliance=device.id,
                until_further_notice=False,
                is_on=True,
                mode=target_mode,
                end_date=end_date,
                temperature_target=target_temp,
            )
        )
