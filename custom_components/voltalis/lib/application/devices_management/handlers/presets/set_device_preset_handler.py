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
from custom_components.voltalis.lib.domain.devices_management.presets.preset_enum import DeviceCurrentPresetEnum
from custom_components.voltalis.lib.domain.devices_management.presets.presets_mappings import PRESET_MODE_MAPPING
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
        default_temperature: float,
        default_away_temperature: float,
        default_eco_temperature: float,
        default_comfort_temperature: float,
    ):
        self.__climate_service = ClimateManagementService(
            logger=logger,
            date_provider=date_provider,
            voltalis_provider=voltalis_provider,
        )
        self.__default_temperature = default_temperature
        self.__default_away_temperature = default_away_temperature
        self.__default_eco_temperature = default_eco_temperature
        self.__default_comfort_temperature = default_comfort_temperature

    async def handle(self, command: SetDevicePresetCommand) -> None:
        """Handle the request to set a preset for a device."""

        if command.device.manual_setting is None:
            raise ValueError(f"Device {command.device.id} does not support manual settings")

        command_preset = command.preset
        # Prevent setting OFF preset if device is not a climate (because climate presets aren't using the real presets)
        if command_preset == DeviceCurrentPresetEnum.OFF and command.climate_mode:
            command_preset = DeviceCurrentPresetEnum.TEMPERATURE

        # Handle AUTO preset - disable manual mode
        if command_preset == DeviceCurrentPresetEnum.AUTO:
            await self.__climate_service.disable_manual_mode(
                manual_setting_id=command.device.manual_setting.id,
                device_id=command.device.id,
                has_device_ecov=command.device.has_ecov,
                fallback_temperature=command.temperature or 16.0,
            )
            return

        # Handle OFF preset
        if command_preset == DeviceCurrentPresetEnum.OFF:
            await self.__climate_service.turn_off(
                manual_setting_id=command.device.manual_setting.id,
                device_id=command.device.id,
                has_device_ecov=command.device.has_ecov,
                fallback_mode=command.device.programming.mode
                if command.device.programming.mode
                else DeviceModeEnum.ECO,
                fallback_temperature=command.temperature or 16.0,
                duration_hours=command.duration_hours,
            )
            return

        if command.has_on_mode and command_preset == DeviceCurrentPresetEnum.ON:
            target_mode = DeviceModeEnum.ON
        else:
            # Handle other presets (COMFORT, ECO, FROST_PROTECTION)
            target_mode = PRESET_MODE_MAPPING.get(command_preset, DeviceModeEnum.ECO)

        temperature = get_appropriate_temperature(
            command.device,
            target_mode,
            default_temperature=self.__default_temperature,
            default_away_temperature=self.__default_away_temperature,
            default_eco_temperature=self.__default_eco_temperature,
            default_comfort_temperature=self.__default_comfort_temperature,
            use_device_programming=target_mode in [DeviceModeEnum.ON, DeviceModeEnum.TEMPERATURE],
            temperature=command.temperature,
        )

        await self.__climate_service.set_manual_mode(
            manual_setting_id=command.device.manual_setting.id,
            device_id=command.device.id,
            has_device_ecov=command.device.has_ecov,
            mode=target_mode,
            temperature_target=temperature,
            duration_hours=command.duration_hours,
        )
