from logging import Logger

from custom_components.voltalis.lib.application.devices_management.commands.set_device_temperature_command import (
    SetDeviceTemperatureCommand,
)
from custom_components.voltalis.lib.application.devices_management.helpers.get_appropriate_temperature import (
    get_appropriate_temperature,
)
from custom_components.voltalis.lib.domain.devices_management.climates.climate_management_service import (
    ClimateManagementService,
)
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class SetDeviceTemperatureHandler:
    """Handler to set target temperature for a climate device."""

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

    async def handle(
        self,
        command: SetDeviceTemperatureCommand,
    ) -> None:
        """Handle the request to set target temperature for a device."""

        target_temp = get_appropriate_temperature(command.device, command.mode, command.temperature)

        await self.__climate_service.set_manual_mode(
            manual_setting_id=command.manual_setting_id,
            device_id=command.device.id,
            mode=command.mode,
            temperature_target=target_temp,
            duration_hours=command.duration_hours,
        )
