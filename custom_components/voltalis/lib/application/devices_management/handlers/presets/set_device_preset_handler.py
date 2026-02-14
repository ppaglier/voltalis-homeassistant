from logging import Logger

from custom_components.voltalis.lib.application.devices_management.commands.set_device_preset_command import (
    SetDevicePresetCommand,
)
from custom_components.voltalis.lib.application.devices_management.helpers.get_appropriate_temperature import (
    get_appropriate_temperature,
)
from custom_components.voltalis.lib.domain.devices_management.climates.climate_management_service import (
    ClimateManagementService,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.presets.device_current_preset_enum import (
    DeviceCurrentPresetEnum,
)
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class SetDevicePresetHandler:
    """Handler to set a preset for a climate device."""

    def __init__(
        self,
        *,
        logger: Logger,
        date_provider: DateProvider,
        voltalis_provider: VoltalisProvider,
    ):
        self.__climate_service = ClimateManagementService(
            logger=logger,
            date_provider=date_provider,
            voltalis_provider=voltalis_provider,
        )

    async def handle(self, command: SetDevicePresetCommand) -> None:
        """Handle the request to set a preset for a device."""

        command_preset = command.preset
        # Prevent setting OFF preset if device is not a climate (because climate presets aren't using the real presets)
        if command_preset == DeviceCurrentPresetEnum.OFF and command.climate_mode:
            command_preset = DeviceCurrentPresetEnum.TEMPERATURE

        # Handle AUTO preset - disable manual mode
        if command_preset == DeviceCurrentPresetEnum.AUTO:
            await self.__climate_service.disable_manual_mode(
                manual_setting_id=command.manual_setting_id,
                device_id=command.device.id,
                fallback_temperature=command.temperature or 16.0,
            )
            return

        # Handle OFF preset
        if command_preset == DeviceCurrentPresetEnum.OFF:
            await self.__climate_service.turn_off(
                manual_setting_id=command.manual_setting_id,
                device_id=command.device.id,
                fallback_temperature=command.temperature or 16.0,
                duration_hours=command.duration_hours,
            )
            return

        if command.has_ecov_mode and command_preset == DeviceCurrentPresetEnum.ECO:
            mode = DeviceModeEnum.ECOV
        elif command.has_on_mode and command_preset == DeviceCurrentPresetEnum.ON:
            mode = DeviceModeEnum.NORMAL
        else:
            # Handle other presets (COMFORT, ECO, FROST_PROTECTION)
            mode_mapping = {
                DeviceCurrentPresetEnum.COMFORT: DeviceModeEnum.CONFORT,
                DeviceCurrentPresetEnum.ECO: DeviceModeEnum.ECO,
                DeviceCurrentPresetEnum.AWAY: DeviceModeEnum.HORS_GEL,
                DeviceCurrentPresetEnum.TEMPERATURE: DeviceModeEnum.TEMPERATURE,
            }
            mode = mode_mapping.get(command_preset, DeviceModeEnum.OFF)  # Default to OFF if preset is unrecognized

        temperature = get_appropriate_temperature(command.device, mode, command.temperature)

        await self.__climate_service.set_manual_mode(
            manual_setting_id=command.manual_setting_id,
            device_id=command.device.id,
            mode=mode,
            temperature_target=temperature,
            duration_hours=command.duration_hours,
        )
