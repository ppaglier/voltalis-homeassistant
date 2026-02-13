from logging import Logger

from homeassistant.components.climate.const import HVACMode

from custom_components.voltalis.lib.application.devices_management.helpers.get_appropriate_temperature import (
    get_appropriate_temperature,
)
from custom_components.voltalis.lib.application.devices_management.queries.set_climate_action_command import (
    SetClimateActionCommand,
)
from custom_components.voltalis.lib.domain.devices_management.climates.climate_management_service import (
    ClimateManagementService,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class SetClimateActionHandler:
    """Handler to set climate action for a device."""

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
        command: SetClimateActionCommand,
    ) -> None:
        """Handle the request to set climate action for a device."""

        target_mode = command.device.programming.mode or DeviceModeEnum.ECO

        target_temp = get_appropriate_temperature(command.device, target_mode)

        match command.action:
            case HVACMode.OFF:
                await self.__climate_service.turn_off(
                    manual_setting_id=command.manual_setting_id,
                    device_id=command.device.id,
                    fallback_mode=target_mode,
                    fallback_temperature=target_temp,
                )
            case HVACMode.HEAT:
                await self.__climate_service.set_manual_mode(
                    manual_setting_id=command.manual_setting_id,
                    device_id=command.device.id,
                    mode=target_mode,
                    temperature_target=target_temp,
                )
            case HVACMode.AUTO:
                await self.__climate_service.disable_manual_mode(
                    manual_setting_id=command.manual_setting_id,
                    device_id=command.device.id,
                    fallback_mode=target_mode,
                    fallback_temperature=target_temp,
                )
            case _:
                raise ValueError(f"HVAC action {command.action} not supported")
