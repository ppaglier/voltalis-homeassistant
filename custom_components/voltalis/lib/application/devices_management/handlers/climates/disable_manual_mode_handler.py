from logging import Logger

from custom_components.voltalis.lib.application.devices_management.commands.disable_manual_mode_command import (
    DisableManualModeCommand,
)
from custom_components.voltalis.lib.application.devices_management.helpers.get_appropriate_temperature import (
    get_appropriate_temperature,
)
from custom_components.voltalis.lib.domain.devices_management.climates.climate_management_service import (
    ClimateManagementService,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class DisableManualModeHandler:
    """Handler to disable manual mode and return to automatic programming."""

    def __init__(
        self,
        *,
        logger: Logger,
        date_provider: DateProvider,
        voltalis_provider: VoltalisProvider,
        default_temperature: float,
        default_away_temp: float,
        default_eco_temp: float,
        default_comfort_temp: float,
    ):
        self.__climate_service = ClimateManagementService(
            logger=logger,
            date_provider=date_provider,
            voltalis_provider=voltalis_provider,
        )
        self.__default_temperature = default_temperature
        self.__default_away_temp = default_away_temp
        self.__default_eco_temp = default_eco_temp
        self.__default_comfort_temp = default_comfort_temp

    async def handle(self, command: DisableManualModeCommand) -> None:
        """Handle the request to disable manual mode for a device."""

        if command.device.manual_setting is None:
            raise ValueError(f"Device {command.device.id} does not support manual settings")

        target_mode = command.fallback_mode or command.device.programming.mode or DeviceModeEnum.ECO

        target_temp = get_appropriate_temperature(
            device=command.device,
            mode=target_mode,
            default_temperature=self.__default_temperature,
            default_away_temperature=self.__default_away_temp,
            default_eco_temperature=self.__default_eco_temp,
            default_comfort_temperature=self.__default_comfort_temp,
            temperature=command.fallback_temperature,
        )

        await self.__climate_service.disable_manual_mode(
            manual_setting_id=command.device.manual_setting.id,
            device_id=command.device.id,
            fallback_mode=command.fallback_mode or command.device.programming.mode or DeviceModeEnum.ECO,
            fallback_temperature=target_temp,
        )
