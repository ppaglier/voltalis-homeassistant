from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from homeassistant.components.water_heater import WaterHeaterEntity, WaterHeaterEntityFeature
from homeassistant.exceptions import HomeAssistantError

from custom_components.voltalis.const import CLIMATE_UNIT
from custom_components.voltalis.lib.domain.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.domain.coordinators.device import VoltalisDeviceCoordinatorData
from custom_components.voltalis.lib.domain.models.device import (
    VoltalisDevice,
    VoltalisDeviceModeEnum,
    VoltalisDeviceProgTypeEnum,
)
from custom_components.voltalis.lib.domain.models.manual_setting import VoltalisManualSettingUpdate
from custom_components.voltalis.lib.domain.voltalis_device_entity import VoltalisDeviceEntity


class VoltalisWaterHeaterOperationsEnum(StrEnum):
    """Enum for water heater operation modes."""

    ON = "on"
    OFF = "off"
    AUTO = "auto"


class VoltalisWaterHeater(VoltalisDeviceEntity, WaterHeaterEntity):
    """Water heater entity for Voltalis water heater devices.

    This is a relay controller with 3 states:
    - ON: Manually forced on
    - OFF: Manually forced off (cut off regardless of HP/HC contactor)
    - AUTO: Voltalis controls the device according to its programming

    Note: When ON, it doesn't mean actively heating - depends on HP/HC contactors.
    """

    _attr_temperature_unit = CLIMATE_UNIT
    _attr_translation_key = "water_heater"
    _unique_id_suffix = "water_heater"

    def __init__(self, entry: VoltalisConfigEntry, device: VoltalisDeviceCoordinatorData) -> None:
        """Initialize the water heater entity."""
        super().__init__(entry, device, entry.runtime_data.coordinators.device)
        # We don't set name there because this is only one entity per device
        # and the device name is already used for the main entity.
        self._attr_name = None

        # Water heater supports ON/OFF and operation modes (ON, OFF, AUTO)
        self._attr_supported_features = (
            WaterHeaterEntityFeature.ON_OFF
            | WaterHeaterEntityFeature.OPERATION_MODE
            | WaterHeaterEntityFeature.AWAY_MODE
        )
        self._attr_operation_list = [operation for operation in VoltalisWaterHeaterOperationsEnum]
        self._attr_is_away_mode_on = False
        self.__before_away_mode_operation: VoltalisWaterHeaterOperationsEnum | None = None

    @property
    def _current_device(self) -> VoltalisDeviceCoordinatorData:
        """Get the current device data from coordinator."""
        device = self._coordinators.device.data.get(self._device.id)
        return device if device else self._device

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        current = self.current_operation
        if current is not None:
            if current == VoltalisWaterHeaterOperationsEnum.ON:
                return "mdi:water-boiler"
            if current == VoltalisWaterHeaterOperationsEnum.OFF:
                return "mdi:water-boiler-off"
            if current == VoltalisWaterHeaterOperationsEnum.AUTO:
                return "mdi:water-boiler-auto"
        return "mdi:water-boiler-alert"

    # ------------------------------------------------------------------
    # Operation mode handling
    # ------------------------------------------------------------------

    @property
    def current_operation(self) -> VoltalisWaterHeaterOperationsEnum | None:
        """Return current operation mode: on, off, or auto."""
        device = self._current_device
        if not device.programming or not device.programming.is_on:
            return VoltalisWaterHeaterOperationsEnum.OFF

        # Check programming type to determine mode
        prog_type = device.programming.prog_type
        if prog_type == VoltalisDeviceProgTypeEnum.MANUAL:
            return VoltalisWaterHeaterOperationsEnum.ON

        # DEFAULT or USER planning means AUTO mode
        return VoltalisWaterHeaterOperationsEnum.AUTO

    async def async_set_operation_mode(self, operation_mode: str) -> None:
        """Set new operation mode: on, off, or auto."""

        self._attr_is_away_mode_on = False

        if operation_mode == VoltalisWaterHeaterOperationsEnum.ON:
            await self.async_turn_on()
            return
        if operation_mode == VoltalisWaterHeaterOperationsEnum.OFF:
            await self.async_turn_off()
            return
        if operation_mode == VoltalisWaterHeaterOperationsEnum.AUTO:
            await self.__disable_manual_mode()
            return
        raise HomeAssistantError(f"Invalid operation mode: {operation_mode}")

    # ------------------------------------------------------------------
    # Away mode handling
    # ------------------------------------------------------------------

    async def async_turn_away_mode_on(self) -> None:
        """Enable away mode by turning off the water heater."""
        self.__before_away_mode_operation = self.current_operation
        await self.async_turn_off()
        self._attr_is_away_mode_on = True

    async def async_turn_away_mode_off(self) -> None:
        """Disable away mode by returning to automatic operation."""
        await self.async_set_operation_mode(self.__before_away_mode_operation or VoltalisWaterHeaterOperationsEnum.AUTO)
        self._attr_is_away_mode_on = False

    # ------------------------------------------------------------------
    # On/Off handling
    # ------------------------------------------------------------------

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the water heater on."""
        await self.__set_manual_mode(is_on=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the water heater off."""
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

    async def __set_manual_mode(self, is_on: bool) -> None:
        """Set manual mode for the device (simple ON/OFF relay)."""
        device = self._current_device

        await self.__update_manual_settings(
            VoltalisManualSettingUpdate(
                enabled=True,  # Enable manual mode
                id_appliance=device.id,
                until_further_notice=True,
                is_on=is_on,
                mode=VoltalisDeviceModeEnum.NORMAL,
                end_date=None,
                temperature_target=device.programming.default_temperature,
            )
        )

    async def __disable_manual_mode(self) -> None:
        """Disable manual mode to return to automatic planning."""
        device = self._current_device

        # Get current settings
        target_mode = VoltalisDeviceModeEnum.AUTO
        target_temp = None

        if device.programming:
            if device.programming.mode:
                target_mode = device.programming.mode
            if device.programming.default_temperature:
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
