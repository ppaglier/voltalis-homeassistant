from logging import Logger

from custom_components.voltalis.lib.application.devices_management.commands.turn_off_device_command import (
    TurnOffDeviceCommand,
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


class TurnOffDeviceHandler:
    """Handler to turn off a climate device for a specified duration."""

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

    async def handle(self, command: TurnOffDeviceCommand) -> None:
        """Handle the request to turn off a device for a specified duration."""

        if command.device.manual_setting is None:
            raise ValueError(f"Device {command.device.id} does not support manual settings")

        target_mode = command.fallback_mode or command.device.programming.mode or DeviceModeEnum.OFF

        target_temp = get_appropriate_temperature(
            device=command.device,
            mode=target_mode,
            default_temperature=self.__default_temperature,
            default_away_temperature=self.__default_away_temperature,
            default_eco_temperature=self.__default_eco_temperature,
            default_comfort_temperature=self.__default_comfort_temperature,
            temperature=command.fallback_temperature,
        )

        await self.__climate_service.turn_off(
            manual_setting_id=command.device.manual_setting.id,
            device_id=command.device.id,
            has_device_ecov=command.device.has_ecov,
            fallback_temperature=target_temp,
            fallback_mode=target_mode,
            duration_hours=command.duration_hours,
        )
