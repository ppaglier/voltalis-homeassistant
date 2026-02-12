from logging import Logger

from custom_components.voltalis.lib.application.devices_management.commands.turn_off_device_command import (
    TurnOffDeviceCommand,
)
from custom_components.voltalis.lib.domain.devices_management.climate.climate_management_service import (
    ClimateManagementService,
)
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
    ):
        self.__climate_service = ClimateManagementService(
            logger=logger,
            date_provider=date_provider,
            voltalis_provider=voltalis_provider,
        )

    async def handle(self, command: TurnOffDeviceCommand) -> None:
        """Handle the request to turn off a device for a specified duration."""

        await self.__climate_service.turn_off(
            manual_setting_id=command.manual_setting_id,
            device_id=command.device_id,
            fallback_temperature=command.fallback_temperature,
            fallback_mode=command.fallback_mode,
            duration_hours=command.duration_hours,
        )
