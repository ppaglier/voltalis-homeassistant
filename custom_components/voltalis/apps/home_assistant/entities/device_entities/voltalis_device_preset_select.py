from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError

from custom_components.voltalis.apps.home_assistant.coordinators.device import DeviceDto
from custom_components.voltalis.apps.home_assistant.entities.base_entities.voltalis_device_entity import (
    VoltalisDeviceEntity,
)
from custom_components.voltalis.apps.home_assistant.entities.config_entry_data import VoltalisConfigEntry
from custom_components.voltalis.lib.application.devices_management.commands.set_device_preset_command import (
    SetDevicePresetCommand,
)
from custom_components.voltalis.lib.application.devices_management.queries.get_device_preset_query import (
    GetDevicePresetQuery,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device import Device
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.device_current_preset_enum import (
    DeviceCurrentPresetEnum,
)


class VoltalisDevicePresetSelect(VoltalisDeviceEntity, SelectEntity):
    """Select entity for Voltalis heating device mode."""

    _attr_translation_key = "device_preset"
    _unique_id_suffix = "device_preset"

    def __init__(self, entry: VoltalisConfigEntry, device: DeviceDto) -> None:
        """Initialize the program select entity."""
        super().__init__(entry, device, entry.runtime_data.voltalis_home_assistant_module.device_coordinator)

        self.__has_ecov_mode = DeviceModeEnum.ECOV in device.available_modes
        self.__has_on_mode = DeviceModeEnum.NORMAL in device.available_modes

        # Build options modes from available modes
        options: list[str] = []
        for voltalis_mode in DeviceCurrentPresetEnum:
            # Skip AUTO | ON | NONE mode here, will add it after the loop
            if voltalis_mode in [
                DeviceCurrentPresetEnum.AUTO,
                DeviceCurrentPresetEnum.ON,
                DeviceCurrentPresetEnum.OFF,
            ]:
                continue

            if voltalis_mode not in device.available_modes:
                # Special handling for ECOV mode
                if (self.__has_ecov_mode and voltalis_mode != DeviceCurrentPresetEnum.ECO) or not self.__has_ecov_mode:
                    continue
                voltalis_mode = DeviceCurrentPresetEnum.ECO

            if voltalis_mode not in options:
                options.append(voltalis_mode)

        self._attr_options = (
            [DeviceCurrentPresetEnum.AUTO]
            + ([DeviceCurrentPresetEnum.ON] if self.__has_on_mode else [])
            + options
            + [DeviceCurrentPresetEnum.OFF]
        )

    @property
    def _current_device(self) -> DeviceDto:
        """Get the current device data from coordinator."""
        device = self._voltalis_module.device_coordinator.data.get(self._device.id)
        return device if device else self._device

    @property
    def icon(self) -> str:
        """Return the icon to use for this entity."""
        current = self.current_option
        if current is not None:
            if current == DeviceCurrentPresetEnum.COMFORT:
                return "mdi:home-thermometer"
            if current == DeviceCurrentPresetEnum.ECO:
                return "mdi:leaf"
            if current == DeviceCurrentPresetEnum.AWAY:
                return "mdi:snowflake-alert"
            if current == DeviceCurrentPresetEnum.TEMPERATURE:
                return "mdi:thermometer"
            if current == DeviceCurrentPresetEnum.ON:
                return "mdi:flash-outline"
            if current == DeviceCurrentPresetEnum.OFF:
                return "mdi:power"
            if current == DeviceCurrentPresetEnum.AUTO:
                return "mdi:autorenew"
        return "mdi:playlist-edit"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        device = self._voltalis_module.device_coordinator.data.get(self._device.id)
        if device is None:
            self._voltalis_module.logger.warning("Device %s not found in coordinator data", self._device.id)
            return

        current_preset = self._voltalis_module._handler.handle(
            GetDevicePresetQuery(
                is_on=device.programming.is_on,
                id_manual_setting=device.programming.id_manual_setting,
                mode=device.programming.mode,
            )
        )

        self._attr_current_option = current_preset
        self.async_write_ha_state()

    async def async_select_option(self, option: str) -> None:
        """Change the selected program mode."""

        device = self._current_device

        # Get manual setting ID
        if not device.manual_setting:
            raise HomeAssistantError(f"Manual setting not available for device {device.id}")

        await self._voltalis_module.set_device_preset_handler.handle(
            SetDevicePresetCommand(
                manual_setting_id=device.manual_setting.id,
                device=device,
                preset=DeviceCurrentPresetEnum(option),
                duration_hours=None,  # Indefinite until user changes it again
                has_ecov_mode=self.__has_ecov_mode,
                has_on_mode=self.__has_on_mode,
            )
        )

        # Refresh coordinator data
        await self.coordinator.async_request_refresh()

    # ------------------------------------------------------------------
    # Availability handling override
    # ------------------------------------------------------------------
    def _is_available_from_data(self, data: Device) -> bool:
        return data.programming.is_on is not None and data.programming.mode is not None
