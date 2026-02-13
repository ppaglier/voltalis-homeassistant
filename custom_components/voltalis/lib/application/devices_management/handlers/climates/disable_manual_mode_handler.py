from logging import Logger

from custom_components.voltalis.lib.application.devices_management.commands.disable_manual_mode_command import (
    DisableManualModeCommand,
)
from custom_components.voltalis.lib.domain.devices_management.climates.climate_management_service import (
    ClimateManagementService,
)
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
    ):
        self.__climate_service = ClimateManagementService(
            logger=logger,
            date_provider=date_provider,
            voltalis_provider=voltalis_provider,
        )

    async def handle(self, command: DisableManualModeCommand) -> None:
        """Handle the request to disable manual mode for a device."""

        await self.__climate_service.disable_manual_mode(
            manual_setting_id=command.manual_setting_id,
            device_id=command.device_id,
            fallback_mode=command.fallback_mode,
            fallback_temperature=command.fallback_temperature,
        )
