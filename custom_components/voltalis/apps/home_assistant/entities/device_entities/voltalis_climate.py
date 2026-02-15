from __future__ import annotations

from typing import Any

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature, HVACAction, HVACMode
from homeassistant.exceptions import HomeAssistantError

from custom_components.voltalis.apps.home_assistant.coordinators.device import DeviceDto
from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_device_entity import (
    VoltalisDeviceEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.const import (
    CLIMATE_BOOST_DURATION,
    CLIMATE_BOOST_TEMP_INCREASE,
    CLIMATE_TEMP_STEP,
    CLIMATE_UNIT,
)
from custom_components.voltalis.lib.application.devices_management.commands.disable_manual_mode_command import (
    DisableManualModeCommand,
)
from custom_components.voltalis.lib.application.devices_management.commands.set_device_preset_command import (
    SetDevicePresetCommand,
)
from custom_components.voltalis.lib.application.devices_management.commands.set_device_temperature_command import (
    SetDeviceTemperatureCommand,
)
from custom_components.voltalis.lib.application.devices_management.commands.turn_off_device_command import (
    TurnOffDeviceCommand,
)
from custom_components.voltalis.lib.application.devices_management.queries.get_climate_action_query import (
    GetClimateActionQuery,
)
from custom_components.voltalis.lib.application.devices_management.queries.get_climate_mode_query import (
    GetClimateModeQuery,
)
from custom_components.voltalis.lib.application.devices_management.queries.get_climate_presets_query import (
    GetClimatePresetsQuery,
)
from custom_components.voltalis.lib.application.devices_management.queries.get_device_preset_query import (
    GetDevicePresetQuery,
)
from custom_components.voltalis.lib.application.devices_management.queries.set_climate_action_command import (
    SetClimateActionCommand,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.device_current_preset_enum import (
    DeviceCurrentPresetEnum,
)


class VoltalisClimate(VoltalisDeviceEntity, ClimateEntity):
    """Climate entity for Voltalis heating devices."""

    _attr_temperature_unit = CLIMATE_UNIT
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.AUTO]
    _attr_target_temperature_step = CLIMATE_TEMP_STEP
    _unique_id_suffix = "climate"

    def __init__(self, entry: VoltalisConfigEntry, device: DeviceDto) -> None:
        """Initialize the climate entity."""
        super().__init__(entry, device, entry.runtime_data.voltalis_home_assistant_module.device_coordinator)
        # We don't set name there because this is only one entity per device
        # and the device name is already used for the main entity.
        self._attr_name = None

        self._attr_min_temp = self._voltalis_module.config.climate_min_temp
        self._attr_max_temp = self._voltalis_module.config.climate_max_temp

        result = self._voltalis_module.get_climate_presets_handler.handle(
            GetClimatePresetsQuery(
                available_modes=device.available_modes,
            )
        )

        self.__has_ecov_mode = result.has_ecov_mode
        self._attr_preset_modes = [preset.value for preset in result.presets]

        # Determine supported features
        features = ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF

        # Add preset mode support if device has available modes other than DeviceCurrentPresetEnum.OFF
        if len(self._attr_preset_modes) > 1:
            features |= ClimateEntityFeature.PRESET_MODE

        # Only add temperature control if device supports TEMPERATURE mode
        if DeviceModeEnum.TEMPERATURE in self._device.available_modes:
            features |= ClimateEntityFeature.TARGET_TEMPERATURE

        self._attr_supported_features = features

    @property
    def _current_device(self) -> DeviceDto:
        """Get the current device data from coordinator."""
        device = self._voltalis_module.device_coordinator.data.get(self._device.id)
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

        await self._voltalis_module.set_device_temperature_handler.handle(
            SetDeviceTemperatureCommand(
                device=self._current_device,
                mode=DeviceModeEnum.TEMPERATURE,
                temperature=temperature,
            )
        )

        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------------------
    # HVAC mode handling
    # ------------------------------------------------------------------

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current HVAC mode."""
        device = self._current_device

        return self._voltalis_module.get_climate_mode_handler.handle(
            GetClimateModeQuery(
                is_on=device.programming.is_on,
                prog_type=device.programming.prog_type,
            )
        )

    @property
    def hvac_action(self) -> HVACAction:
        """Return current HVAC action."""
        device = self._current_device

        return self._voltalis_module.get_climate_action_handler.handle(
            GetClimateActionQuery(
                is_on=device.programming.is_on,
                mode=device.programming.mode,
            )
        )

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""

        mode_to_action = {
            HVACMode.OFF: HVACAction.OFF,
            HVACMode.HEAT: HVACAction.HEATING,
            HVACMode.AUTO: HVACAction.IDLE,
        }

        await self._voltalis_module.set_climate_action_handler.handle(
            SetClimateActionCommand(
                device=self._current_device,
                action=mode_to_action[hvac_mode],
            )
        )

        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        """Turn the entity on."""

        await self._voltalis_module.set_device_temperature_handler.handle(
            SetDeviceTemperatureCommand(
                device=self._current_device,
                mode=self._current_device.programming.mode or DeviceModeEnum.ECO,
            )
        )

        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the entity off."""

        await self._voltalis_module.turn_off_device_handler.handle(TurnOffDeviceCommand(device=self._current_device))

        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------------------
    # Preset mode handling
    # ------------------------------------------------------------------

    @property
    def preset_mode(self) -> str | None:
        """Return current preset mode."""
        device = self._current_device

        if device.manual_setting is None:
            raise HomeAssistantError(f"Device {device.id} does not support manual settings")

        return self._voltalis_module.get_device_preset_handler.handle(
            GetDevicePresetQuery(
                is_on=device.programming.is_on,
                id_manual_setting=device.manual_setting.id,
                mode=device.programming.mode,
                climate_mode=True,
            )
        )

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""

        await self._voltalis_module.set_device_preset_handler.handle(
            SetDevicePresetCommand(
                device=self._current_device,
                preset=DeviceCurrentPresetEnum(preset_mode),
                has_ecov_mode=self.__has_ecov_mode,
                climate_mode=True,
            )
        )

        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: Device) -> bool:
        return data.programming.is_on is not None and data.programming.mode is not None

    # ------------------------------------------------------------------
    # Service action methods
    # ------------------------------------------------------------------
    async def async_service_set_manual_mode(
        self,
        preset_mode: DeviceCurrentPresetEnum | None = None,
        temperature: float | None = None,
        duration_hours: int | None = None,
    ) -> None:
        """Service action to set manual mode with preset or temperature."""

        if preset_mode is not None:
            await self._voltalis_module.set_device_preset_handler.handle(
                SetDevicePresetCommand(
                    device=self._current_device,
                    temperature=temperature,
                    preset=preset_mode,
                    has_ecov_mode=self.__has_ecov_mode,
                    duration_hours=duration_hours,
                )
            )

            # Refresh coordinator data
            await self.coordinator.async_request_refresh()

            return

        target_mode = self._current_device.programming.mode or DeviceModeEnum.ECO
        # Determine the mode to use
        if temperature is not None:
            # Use TEMPERATURE mode if temperature is specified
            target_mode = DeviceModeEnum.TEMPERATURE

        await self._voltalis_module.set_device_temperature_handler.handle(
            SetDeviceTemperatureCommand(
                device=self._current_device,
                mode=target_mode,
                duration_hours=duration_hours,
            )
        )

        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    async def async_service_disable_manual_mode(self) -> None:
        """Service action to disable manual mode and return to automatic planning."""

        await self._voltalis_module.disable_manual_mode_handler.handle(
            DisableManualModeCommand(device=self._current_device)
        )

    async def async_service_set_quick_boost(
        self,
        duration_hours: float = CLIMATE_BOOST_DURATION,
        temperature: float | None = None,
    ) -> None:
        """Service action to quickly boost heating for a short period."""
        device = self._current_device

        if device.manual_setting is None:
            raise HomeAssistantError(f"Device {device.id} does not support manual settings")

        target_mode = DeviceModeEnum.CONFORT
        target_temp = self._voltalis_module.config.default_comfort_temp + CLIMATE_BOOST_TEMP_INCREASE

        # If the device isn't in temperature mode, we can boost by increasing the target temperature above comfort temp
        if self.preset_mode == DeviceCurrentPresetEnum.OFF and device.programming.temperature_target is not None:
            target_temp = device.programming.temperature_target + CLIMATE_BOOST_TEMP_INCREASE

        # Determine the mode to use
        if temperature is not None:
            # Use TEMPERATURE mode if temperature is specified
            target_mode = DeviceModeEnum.TEMPERATURE
            target_temp = temperature

        await self._voltalis_module.set_device_temperature_handler.handle(
            SetDeviceTemperatureCommand(
                device=device,
                mode=target_mode,
                temperature=target_temp,
                duration_hours=duration_hours,
            )
        )

        # Refresh coordinator data
        await self.coordinator.async_request_refresh()
