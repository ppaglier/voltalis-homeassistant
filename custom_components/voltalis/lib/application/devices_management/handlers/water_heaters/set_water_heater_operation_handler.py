from logging import Logger

from custom_components.voltalis.lib.application.devices_management.commands.set_water_heater_operation_command import (
    SetWaterHeaterOperationCommand,
)
from custom_components.voltalis.lib.application.devices_management.helpers.get_appropriate_temperature import (
    get_appropriate_temperature,
)
from custom_components.voltalis.lib.domain.devices_management.climates.climate_management_service import (
    ClimateManagementService,
)
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.devices_management.water_heaters.water_heater_current_operations_enum import (  # noqa: E501
    WaterHeaterCurrentOperationEnum,
)
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class SetWaterHeaterOperationHandler:
    """Handler to set a preset for a climate device."""

    def __init__(
        self,
        *,
        logger: Logger,
        date_provider: DateProvider,
        voltalis_provider: VoltalisProvider,
        default_water_heater_temp: float,
    ):
        self.__logger = logger
        self.__climate_service = ClimateManagementService(
            logger=logger,
            date_provider=date_provider,
            voltalis_provider=voltalis_provider,
        )
        self.__default_water_heater_temp = default_water_heater_temp

    async def handle(self, command: SetWaterHeaterOperationCommand) -> None:

        if command.device.manual_setting is None:
            raise ValueError(f"Device {command.device.id} does not support manual settings")

        match command.operation_mode:
            case WaterHeaterCurrentOperationEnum.ON:
                await self.__turn_on(command, command.device.manual_setting.id)
                return
            case WaterHeaterCurrentOperationEnum.OFF:
                await self.__turn_off(command, command.device.manual_setting.id)
                return
            case WaterHeaterCurrentOperationEnum.AUTO:
                await self.__turn_auto_mode(command, command.device.manual_setting.id)
                return
            case _:
                self.__logger.error(f"Invalid operation mode: {command.operation_mode}")

    async def __turn_on(self, command: SetWaterHeaterOperationCommand, manual_setting_id: int) -> None:
        """Set OFF mode by turning off the water heater with a manual mode."""

        target_mode = DeviceModeEnum.NORMAL

        target_temp = get_appropriate_temperature(
            command.device,
            target_mode,
            default_temperature=self.__default_water_heater_temp,
            default_away_temperature=self.__default_water_heater_temp,
            default_eco_temperature=self.__default_water_heater_temp,
            default_comfort_temperature=self.__default_water_heater_temp,
        )

        await self.__climate_service.set_manual_mode(
            manual_setting_id=manual_setting_id,
            device_id=command.device.id,
            mode=target_mode,
            temperature_target=target_temp,
            duration_hours=None,
        )

    async def __turn_off(self, command: SetWaterHeaterOperationCommand, manual_setting_id: int) -> None:
        """Set OFF mode by turning off the water heater with a manual mode."""

        target_mode = DeviceModeEnum.NORMAL

        target_temp = get_appropriate_temperature(
            command.device,
            target_mode,
            default_temperature=self.__default_water_heater_temp,
            default_away_temperature=self.__default_water_heater_temp,
            default_eco_temperature=self.__default_water_heater_temp,
            default_comfort_temperature=self.__default_water_heater_temp,
        )

        await self.__climate_service.turn_off(
            manual_setting_id=manual_setting_id,
            device_id=command.device.id,
            fallback_mode=target_mode,
            fallback_temperature=target_temp,
            duration_hours=None,
        )

    async def __turn_auto_mode(self, command: SetWaterHeaterOperationCommand, manual_setting_id: int) -> None:
        """Set AUTO mode to return to automatic planning."""

        target_mode = DeviceModeEnum.AUTO
        if command.device.programming.mode:
            target_mode = command.device.programming.mode

        target_temp = get_appropriate_temperature(
            command.device,
            target_mode,
            default_temperature=self.__default_water_heater_temp,
            default_away_temperature=self.__default_water_heater_temp,
            default_eco_temperature=self.__default_water_heater_temp,
            default_comfort_temperature=self.__default_water_heater_temp,
        )

        await self.__climate_service.disable_manual_mode(
            manual_setting_id=manual_setting_id,
            device_id=command.device.id,
            fallback_mode=target_mode,
            fallback_temperature=target_temp,
        )
