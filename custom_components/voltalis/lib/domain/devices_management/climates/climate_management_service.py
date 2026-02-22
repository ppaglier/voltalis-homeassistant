from datetime import datetime, timedelta
from logging import Logger

from custom_components.voltalis.lib.domain.devices_management.climates.manual_setting import ManualSettingUpdate
from custom_components.voltalis.lib.domain.devices_management.devices.device_enum import DeviceModeEnum
from custom_components.voltalis.lib.domain.shared.providers.date_provider import DateProvider
from custom_components.voltalis.lib.domain.shared.providers.voltalis_provider import VoltalisProvider


class ClimateManagementService:
    """Service to manage climate device manual settings."""

    def __init__(
        self,
        *,
        logger: Logger,
        date_provider: DateProvider,
        voltalis_provider: VoltalisProvider,
    ):
        self.__logger = logger
        self.__date_provider = date_provider
        self.__voltalis_provider = voltalis_provider

    async def set_manual_mode(
        self,
        *,
        manual_setting_id: int,
        device_id: int,
        has_device_ecov: bool,
        mode: DeviceModeEnum,
        temperature_target: float,
        is_on: bool = True,
        duration_hours: int | None = None,
    ) -> None:
        """Set manual mode for a device.

        Args:
            manual_setting_id: The ID of the manual setting to update
            device_id: The ID of the device (appliance)
            mode: The device mode to set
            temperature_target: The target temperature
            is_on: Whether the device should be turned on (default: True)
            duration_hours: Duration in hours (None = indefinite)
        """

        end_date, until_further_notice = self.__calculate_end_date(duration_hours)

        setting = ManualSettingUpdate(
            enabled=True,
            id_appliance=device_id,
            until_further_notice=until_further_notice,
            is_on=is_on,
            has_ecov=has_device_ecov,
            mode=mode,
            end_date=end_date,
            temperature_target=temperature_target,
        )

        await self.__voltalis_provider.set_manual_setting(manual_setting_id, setting)

        self.__logger.info(
            "Manual mode set for device %s: mode=%s, temperature=%.1f°C, duration=%s hours",
            device_id,
            mode.value,
            temperature_target,
            duration_hours or "indefinite",
        )

    async def disable_manual_mode(
        self,
        *,
        manual_setting_id: int,
        device_id: int,
        has_device_ecov: bool,
        fallback_mode: DeviceModeEnum = DeviceModeEnum.ECO,
        fallback_temperature: float = 16.0,
    ) -> None:
        """Disable manual mode and return to automatic programming.

        Args:
            manual_setting_id: The ID of the manual setting to update
            device_id: The ID of the device (appliance)
            fallback_mode: The mode to use as fallback (default: ECO)
            fallback_temperature: The temperature to use as fallback (default: 16.0°C)
        """

        end_date = self.__date_provider.get_now().replace(
            microsecond=0
        )  # End date is now, we want to avoid microsecond differences

        setting = ManualSettingUpdate(
            enabled=False,
            id_appliance=device_id,
            until_further_notice=False,
            is_on=True,
            has_ecov=has_device_ecov,
            mode=fallback_mode,
            end_date=end_date,
            temperature_target=fallback_temperature,
        )

        await self.__voltalis_provider.set_manual_setting(manual_setting_id, setting)

        self.__logger.info(
            "Manual mode disabled for device %s, returning to automatic programming",
            device_id,
        )

    async def turn_off(
        self,
        *,
        manual_setting_id: int,
        device_id: int,
        has_device_ecov: bool,
        fallback_mode: DeviceModeEnum = DeviceModeEnum.ECO,
        fallback_temperature: float = 16.0,
        duration_hours: int | None = None,
    ) -> None:
        """Turn off the device.

        Args:
            manual_setting_id: The ID of the manual setting to update
            device_id: The ID of the device (appliance)
            fallback_mode: The mode to use as fallback when turning off
            fallback_temperature: The temperature to use as fallback when turning off
            duration_hours: Duration in hours (None = indefinite)
        """

        end_date, until_further_notice = self.__calculate_end_date(duration_hours)

        setting = ManualSettingUpdate(
            enabled=True,
            id_appliance=device_id,
            until_further_notice=until_further_notice,
            is_on=False,
            has_ecov=has_device_ecov,
            mode=fallback_mode,
            end_date=end_date,
            temperature_target=fallback_temperature,
        )

        await self.__voltalis_provider.set_manual_setting(manual_setting_id, setting)

    def __calculate_end_date(self, duration_hours: int | None) -> tuple[datetime | None, bool]:
        """Calculate end date and until_further_notice flag based on duration.

        Args:
            duration_hours: Duration in hours or None for indefinite

        Returns:
            Tuple of (end_date, until_further_notice)
        """

        if duration_hours is None:
            return None, True

        now = self.__date_provider.get_now().replace(microsecond=0)
        end_date = now + timedelta(hours=duration_hours)
        return end_date, False
